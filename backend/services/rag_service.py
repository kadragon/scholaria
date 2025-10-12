"""
FastAPI RAG Service.

Async version of Django RAGService with Redis caching.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from collections.abc import AsyncGenerator
from typing import Any

import redis.asyncio as redis
from openai import AsyncOpenAI
from sqlalchemy.orm import Session

from backend.models.base import get_db
from backend.models.history import QuestionHistory
from backend.observability import get_meter, get_tracer
from backend.retrieval.embeddings import EmbeddingService
from backend.retrieval.monitoring import OpenAIUsageMonitor
from backend.retrieval.qdrant import QdrantService
from backend.retrieval.reranking import RerankingService

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)
meter = get_meter(__name__)


class AsyncRAGService:
    """Async RAG query pipeline service."""

    def __init__(
        self,
        redis_client: redis.Redis,
        openai_api_key: str,
        openai_chat_model: str = "gpt-4o-mini",
        openai_chat_temperature: float = 0.3,
        openai_chat_max_tokens: int = 1000,
        rag_search_limit: int = 10,
        rag_rerank_top_k: int = 5,
    ) -> None:
        self.redis_client = redis_client
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()
        self.qdrant_service.create_collection()
        self.reranking_service = RerankingService()
        self.chat_client = AsyncOpenAI(api_key=openai_api_key)
        self.monitor = OpenAIUsageMonitor()

        self.openai_chat_model = openai_chat_model
        self.openai_chat_temperature = openai_chat_temperature
        self.openai_chat_max_tokens = openai_chat_max_tokens
        self.rag_search_limit = rag_search_limit
        self.rag_rerank_top_k = rag_rerank_top_k

        self._query_duration_histogram = meter.create_histogram(
            name="rag.query.duration",
            description="Duration of RAG query pipeline execution",
            unit="s",
        )
        self._query_errors_counter = meter.create_counter(
            name="rag.query.errors",
            description="Total number of RAG query errors",
        )
        self._vector_search_results_histogram = meter.create_histogram(
            name="rag.vector_search.results",
            description="Number of vector search results",
        )
        self._openai_tokens_counter = meter.create_counter(
            name="rag.openai.tokens",
            description="Total number of OpenAI tokens used",
        )

    def _get_query_cache_key(
        self, query: str, topic_ids: list[int], limit: int, rerank_top_k: int
    ) -> str:
        """Generate a cache key for a query combination."""
        cache_data = {
            "query": query.strip().lower(),
            "topic_ids": sorted(topic_ids),
            "limit": limit,
            "rerank_top_k": rerank_top_k,
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
        return f"rag_query:{cache_hash}"

    async def _get_cached_result(self, cache_key: str) -> dict[str, Any] | None:
        """Get cached query result."""
        cached = await self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        return None

    async def _cache_result(self, cache_key: str, result: dict[str, Any]) -> None:
        """Cache query result for 15 minutes."""
        await self.redis_client.set(cache_key, json.dumps(result), ex=900)

    async def query(
        self,
        query: str | None,
        topic_ids: list[int],
        limit: int | None = None,
        rerank_top_k: int | None = None,
    ) -> dict[str, Any]:
        """
        Execute a complete RAG query pipeline with caching.

        Args:
            query: User's question
            topic_ids: List of topic IDs to search within
            limit: Maximum number of initial search results
            rerank_top_k: Maximum number of results after reranking

        Returns:
            Dictionary containing answer, sources, and context items

        Raises:
            ValueError: If query is None/empty or topic_ids is empty
        """
        start_time = time.perf_counter()
        with tracer.start_as_current_span("rag.query") as span:
            try:
                if query is None or not query.strip():
                    raise ValueError("Query cannot be None or empty")

                if not topic_ids:
                    raise ValueError("Topic IDs cannot be empty")

                span.set_attribute("query.length", len(query))
                span.set_attribute("topic_ids.count", len(topic_ids))

                limit = limit if limit is not None else self.rag_search_limit
                rerank_top_k = (
                    rerank_top_k if rerank_top_k is not None else self.rag_rerank_top_k
                )

                span.set_attribute("search.limit", limit)
                span.set_attribute("rerank.top_k", rerank_top_k)

                # Check cache first
                cache_key = self._get_query_cache_key(
                    query, topic_ids, limit, rerank_top_k
                )
                cached_result = await self._get_cached_result(cache_key)
                if cached_result is not None:
                    span.set_attribute("cache.hit", True)
                    return cached_result

                span.set_attribute("cache.hit", False)

                # Step 1: Generate embedding for the query (blocking, but fast)
                query_embedding = await asyncio.to_thread(
                    self.embedding_service.generate_embedding, query
                )

                # Step 2: Search for similar context items in Qdrant (SQLAlchemy-backed lookups)
                search_results = await asyncio.to_thread(
                    self.qdrant_service.search_similar,
                    query_embedding=query_embedding,
                    topic_ids=topic_ids,
                    limit=limit,
                )

                self._vector_search_results_histogram.record(len(search_results))

                # If no results found, return empty response
                if not search_results:
                    span.set_attribute("results.count", 0)
                    result = {
                        "answer": "I couldn't find any relevant information for your question in the selected topics.",
                        "sources": [],
                        "context_items": [],
                    }
                    # Cache empty results for shorter duration (5 minutes)
                    await self.redis_client.set(cache_key, json.dumps(result), ex=300)
                    return result

                # Step 3: Rerank results using BGE reranker (blocking, ML model)
                reranked_results = await asyncio.to_thread(
                    self.reranking_service.rerank_results,
                    query=query,
                    search_results=search_results,
                    top_k=rerank_top_k,
                )

                span.set_attribute("results.count", len(reranked_results))

                # Step 4: Prepare context for the LLM
                context_text = self._prepare_context(reranked_results)

                # Step 5: Generate answer using OpenAI
                answer, usage = await self._generate_answer(query, context_text)

                if usage:
                    self._openai_tokens_counter.add(
                        usage.get("prompt_tokens", 0), {"type": "prompt"}
                    )
                    self._openai_tokens_counter.add(
                        usage.get("completion_tokens", 0), {"type": "completion"}
                    )

                # Step 6: Format response
                sources = [
                    {
                        "title": result["title"],
                        "content": result["content"],
                        "score": result.get("rerank_score", result.get("score", 0.0)),
                        "context_type": result.get("context_type", ""),
                        "context_item_id": result["context_item_id"],
                    }
                    for result in reranked_results
                ]

                final_result: dict[str, Any] = {
                    "answer": answer,
                    "sources": sources,
                    "context_items": reranked_results,
                }

                # Cache the result
                await self._cache_result(cache_key, final_result)

                return final_result

            except Exception:
                self._query_errors_counter.add(1, {"stage": "query"})
                raise
            finally:
                duration = time.perf_counter() - start_time
                self._query_duration_histogram.record(duration)

    def _prepare_context(self, search_results: list[dict[str, Any]]) -> str:
        """Prepare context text from search results for the LLM."""
        if not search_results:
            return ""

        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"[Source {i}] {result['title']}\n{result['content']}\n"
            )

        return "\n".join(context_parts)

    async def _generate_answer(
        self, query: str, context: str
    ) -> tuple[str, dict[str, int]]:
        """Generate an answer using OpenAI API."""
        with tracer.start_as_current_span("rag.llm_generation") as span:
            if not context:
                return (
                    "I couldn't find any relevant information to answer your question.",
                    {},
                )

            # Create the prompt
            prompt = f"""You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above. If the context doesn't contain enough information to fully answer the question, acknowledge this in your response. Include relevant details from the sources where appropriate."""

            span.set_attribute("model.name", self.openai_chat_model)
            span.set_attribute("prompt.length", len(prompt))

            # Track request timing for rate limiting
            self.monitor.track_request_timestamp("chat_completions")

            response = await self.chat_client.chat.completions.create(
                model=self.openai_chat_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides accurate answers based on the given context.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.openai_chat_temperature,
                max_tokens=self.openai_chat_max_tokens,
            )

            # Track usage metrics
            prompt_tokens = 0
            completion_tokens = 0
            if hasattr(response, "usage") and response.usage:
                prompt_tokens = (
                    int(response.usage.prompt_tokens)
                    if hasattr(response.usage, "prompt_tokens")
                    else 0
                )
                completion_tokens = (
                    int(response.usage.completion_tokens)
                    if hasattr(response.usage, "completion_tokens")
                    else 0
                )
                span.set_attribute("tokens.prompt", prompt_tokens)
                span.set_attribute("tokens.completion", completion_tokens)
                span.set_attribute("tokens.total", prompt_tokens + completion_tokens)
                self.monitor.track_chat_completion_usage(
                    prompt_tokens, completion_tokens, self.openai_chat_model
                )
            else:
                # Estimate tokens if usage not available
                prompt_tokens = len(prompt) // 4
                completion_tokens = 100
                span.set_attribute("tokens.prompt", prompt_tokens)
                span.set_attribute("tokens.completion", completion_tokens)
                self.monitor.track_chat_completion_usage(
                    prompt_tokens,
                    completion_tokens,
                    self.openai_chat_model,
                )

            answer = (
                response.choices[0].message.content
                or "I apologize, but I couldn't generate an answer at this time."
            )
            span.set_attribute("answer.length", len(answer))

            usage_info = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            }

            return answer, usage_info

    async def _get_conversation_history(
        self, session_id: str, current_question: str, db: Session
    ) -> str:
        """Retrieve and format conversation history for the current session."""
        try:
            histories = await asyncio.to_thread(
                lambda: db.query(QuestionHistory)
                .filter(QuestionHistory.session_id == session_id)
                .order_by(QuestionHistory.created_at.asc())
                .all()
            )

            if not histories:
                return ""

            # Format conversation history, excluding the current question if it's already in history
            conversation_parts = []
            for history in histories:
                # Skip if this is the current question being asked
                if history.question.strip().lower() == current_question.strip().lower():
                    continue

                conversation_parts.append(f"User: {history.question}")
                conversation_parts.append(f"Assistant: {history.answer}")

            return (
                "\n\n".join(conversation_parts) + "\n\n" if conversation_parts else ""
            )
        except Exception as e:
            logger.warning("Failed to retrieve conversation history: %s", str(e))
            return ""

    async def query_stream(
        self,
        query: str,
        topic_ids: list[int],
        session_id: str | None = None,
        limit: int | None = None,
        rerank_top_k: int | None = None,
    ) -> AsyncGenerator[str]:
        """
        Execute RAG query with streaming response.

        Yields SSE-formatted JSON events:
        - {"type": "answer_chunk", "content": str, "chunk_index": int}
        - {"type": "citations", "citations": list[dict]}
        - {"type": "done"}
        - {"type": "error", "message": str}
        """
        if not query or not query.strip():
            yield json.dumps({"type": "error", "message": "Query cannot be empty"})
            return

        if not topic_ids:
            yield json.dumps({"type": "error", "message": "Topic IDs cannot be empty"})
            return

        try:
            limit = limit if limit is not None else self.rag_search_limit
            rerank_top_k = (
                rerank_top_k if rerank_top_k is not None else self.rag_rerank_top_k
            )

            # Get conversation history if session_id is provided
            conversation_history = ""
            if session_id:
                db = next(get_db())
                try:
                    conversation_history = await self._get_conversation_history(
                        session_id, query, db
                    )
                finally:
                    db.close()

            query_embedding = await asyncio.to_thread(
                self.embedding_service.generate_embedding, query
            )

            search_results = await asyncio.to_thread(
                self.qdrant_service.search_similar,
                query_embedding=query_embedding,
                topic_ids=topic_ids,
                limit=limit,
            )

            if not search_results:
                yield json.dumps(
                    {
                        "type": "answer_chunk",
                        "content": "I couldn't find any relevant information for your question.",
                        "chunk_index": 0,
                    }
                )
                yield json.dumps({"type": "citations", "citations": []})
                yield json.dumps({"type": "done"})
                return

            reranked_results = await asyncio.to_thread(
                self.reranking_service.rerank_results,
                query=query,
                search_results=search_results,
                top_k=rerank_top_k,
            )

            context_text = self._prepare_context(reranked_results)

            chunk_index = 0
            async for chunk in self._generate_answer_stream(
                query, context_text, conversation_history
            ):
                yield json.dumps(
                    {
                        "type": "answer_chunk",
                        "content": chunk,
                        "chunk_index": chunk_index,
                    }
                )
                chunk_index += 1

            citations = [
                {
                    "title": result["title"],
                    "content": result["content"],
                    "score": result.get("rerank_score", result.get("score", 0.0)),
                    "context_type": result.get("context_type", ""),
                    "context_item_id": result["context_item_id"],
                }
                for result in reranked_results
            ]
            yield json.dumps({"type": "citations", "citations": citations})
            yield json.dumps({"type": "done"})

        except Exception as e:
            logger.error("RAG streaming error: %s", str(e), exc_info=True)
            yield json.dumps(
                {
                    "type": "error",
                    "message": "An error occurred while processing your request",
                }
            )

    async def _generate_answer_stream(
        self, query: str, context: str, conversation_history: str = ""
    ) -> AsyncGenerator[str]:
        """Generate streaming answer using OpenAI API."""
        if not context:
            yield "I couldn't find any relevant information to answer your question."
            return

        # Build prompt with conversation history if available
        prompt_parts = [
            "You are a helpful assistant that answers questions based on the provided context."
        ]

        if conversation_history:
            prompt_parts.append(f"\nPrevious conversation:\n{conversation_history}")

        prompt_parts.extend(
            [
                f"\nContext:\n{context}",
                f"\nQuestion: {query}",
                "\nPlease provide a comprehensive answer based on the context above. If the context doesn't contain enough information to fully answer the question, acknowledge this in your response. Include relevant details from the sources where appropriate.",
            ]
        )

        prompt = "".join(prompt_parts)

        self.monitor.track_request_timestamp("chat_completions")

        stream = await self.chat_client.chat.completions.create(
            model=self.openai_chat_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides accurate answers based on the given context.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=self.openai_chat_temperature,
            max_tokens=self.openai_chat_max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
