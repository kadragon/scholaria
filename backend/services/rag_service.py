"""
FastAPI RAG Service.

Async version of Django RAGService with Redis caching.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import redis.asyncio as redis
from openai import AsyncOpenAI

from backend.retrieval.embeddings import EmbeddingService
from backend.retrieval.monitoring import OpenAIUsageMonitor
from backend.retrieval.qdrant import QdrantService
from backend.retrieval.reranking import RerankingService


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
        if query is None or not query.strip():
            raise ValueError("Query cannot be None or empty")

        if not topic_ids:
            raise ValueError("Topic IDs cannot be empty")

        limit = limit if limit is not None else self.rag_search_limit
        rerank_top_k = (
            rerank_top_k if rerank_top_k is not None else self.rag_rerank_top_k
        )

        # Check cache first
        cache_key = self._get_query_cache_key(query, topic_ids, limit, rerank_top_k)
        cached_result = await self._get_cached_result(cache_key)
        if cached_result is not None:
            return cached_result

        # Step 1: Generate embedding for the query (blocking, but fast)
        from asgiref.sync import sync_to_async

        query_embedding = await sync_to_async(
            self.embedding_service.generate_embedding
        )(query)

        # Step 2: Search for similar context items in Qdrant (has Django ORM calls)
        search_results = await sync_to_async(self.qdrant_service.search_similar)(
            query_embedding=query_embedding, topic_ids=topic_ids, limit=limit
        )

        # If no results found, return empty response
        if not search_results:
            result = {
                "answer": "I couldn't find any relevant information for your question in the selected topics.",
                "sources": [],
                "context_items": [],
            }
            # Cache empty results for shorter duration (5 minutes)
            await self.redis_client.set(cache_key, json.dumps(result), ex=300)
            return result

        # Step 3: Rerank results using BGE reranker (blocking, ML model)
        reranked_results = await sync_to_async(self.reranking_service.rerank_results)(
            query=query, search_results=search_results, top_k=rerank_top_k
        )

        # Step 4: Prepare context for the LLM
        context_text = self._prepare_context(reranked_results)

        # Step 5: Generate answer using OpenAI
        answer = await self._generate_answer(query, context_text)

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

    async def _generate_answer(self, query: str, context: str) -> str:
        """Generate an answer using OpenAI API."""
        if not context:
            return "I couldn't find any relevant information to answer your question."

        # Create the prompt
        prompt = f"""You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above. If the context doesn't contain enough information to fully answer the question, acknowledge this in your response. Include relevant details from the sources where appropriate."""

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
            self.monitor.track_chat_completion_usage(
                prompt_tokens, completion_tokens, self.openai_chat_model
            )
        else:
            # Estimate tokens if usage not available
            estimated_prompt_tokens = len(prompt) // 4
            estimated_completion_tokens = 100
            self.monitor.track_chat_completion_usage(
                estimated_prompt_tokens,
                estimated_completion_tokens,
                self.openai_chat_model,
            )

        return (
            response.choices[0].message.content
            or "I apologize, but I couldn't generate an answer at this time."
        )
