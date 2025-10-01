from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING, Any

import openai
from django.conf import settings
from django.core.cache import cache

from .embeddings import EmbeddingService
from .monitoring import OpenAIUsageMonitor
from .qdrant import QdrantService
from .reranking import RerankingService

if TYPE_CHECKING:
    pass


class RAGService:
    """Complete RAG query pipeline service."""

    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()
        # Ensure Qdrant collection exists
        self.qdrant_service.create_collection()
        self.reranking_service = RerankingService()
        self.chat_client = openai.OpenAI(
            api_key=getattr(settings, "OPENAI_API_KEY", None)
        )
        self.monitor = OpenAIUsageMonitor()

    def _get_query_cache_key(
        self, query: str, topic_ids: list[int], limit: int, rerank_top_k: int
    ) -> str:
        """
        Generate a cache key for a query combination.

        Args:
            query: User's question
            topic_ids: List of topic IDs
            limit: Search limit
            rerank_top_k: Rerank top k

        Returns:
            Cache key string
        """
        # Create a deterministic cache key from query parameters
        cache_data = {
            "query": query.strip().lower(),
            "topic_ids": sorted(topic_ids),
            "limit": limit,
            "rerank_top_k": rerank_top_k,
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
        return f"rag_query:{cache_hash}"

    def _get_cached_result(self, cache_key: str) -> dict[str, Any] | None:
        """
        Get cached query result.

        Args:
            cache_key: Cache key for the query

        Returns:
            Cached result or None if not found
        """
        return cache.get(cache_key)

    def _cache_result(self, cache_key: str, result: dict[str, Any]) -> None:
        """
        Cache query result.

        Args:
            cache_key: Cache key for the query
            result: Query result to cache
        """
        # Cache for 15 minutes to balance freshness and performance
        cache.set(cache_key, result, 900)

    def query(
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

        # Use settings for default values if not provided
        limit = (
            limit if limit is not None else getattr(settings, "RAG_SEARCH_LIMIT", 10)
        )
        rerank_top_k = (
            rerank_top_k
            if rerank_top_k is not None
            else getattr(settings, "RAG_RERANK_TOP_K", 5)
        )

        # Check cache first
        cache_key = self._get_query_cache_key(query, topic_ids, limit, rerank_top_k)
        cached_result = self._get_cached_result(cache_key)
        if cached_result is not None:
            return cached_result

        # Step 1: Generate embedding for the query
        query_embedding = self.embedding_service.generate_embedding(query)

        # Step 2: Search for similar context items in Qdrant
        search_results = self.qdrant_service.search_similar(
            query_embedding=query_embedding, topic_ids=topic_ids, limit=limit
        )

        # If no results found, return empty response
        if not search_results:
            result = {
                "answer": "I couldn't find any relevant information for your question in the selected topics.",
                "sources": [],
                "context_items": [],
            }
            # Cache empty results for shorter duration
            cache.set(cache_key, result, 300)  # 5 minutes
            return result

        # Step 3: Rerank results using BGE reranker
        reranked_results = self.reranking_service.rerank_results(
            query=query, search_results=search_results, top_k=rerank_top_k
        )

        # Step 4: Prepare context for the LLM
        context_text = self._prepare_context(reranked_results)

        # Step 5: Generate answer using OpenAI
        answer = self._generate_answer(query, context_text)

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
        self._cache_result(cache_key, final_result)

        return final_result

    def _prepare_context(self, search_results: list[dict[str, Any]]) -> str:
        """
        Prepare context text from search results for the LLM.

        Args:
            search_results: List of search results with content

        Returns:
            Formatted context text
        """
        if not search_results:
            return ""

        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"[Source {i}] {result['title']}\n{result['content']}\n"
            )

        return "\n".join(context_parts)

    def _generate_answer(self, query: str, context: str) -> str:
        """
        Generate an answer using OpenAI API.

        Args:
            query: User's question
            context: Context information from search results

        Returns:
            Generated answer
        """
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

        model = getattr(settings, "OPENAI_CHAT_MODEL", "gpt-4o-mini")
        response = self.chat_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides accurate answers based on the given context.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=getattr(settings, "OPENAI_CHAT_TEMPERATURE", 0.3),
            max_tokens=getattr(settings, "OPENAI_CHAT_MAX_TOKENS", 1000),
        )

        # Track usage metrics
        if hasattr(response, "usage") and response.usage:
            # Ensure we get integers rather than MagicMock objects in tests
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
                prompt_tokens, completion_tokens, model
            )
        else:
            # Estimate tokens if usage not available
            estimated_prompt_tokens = len(prompt) // 4
            estimated_completion_tokens = 100  # Conservative estimate
            self.monitor.track_chat_completion_usage(
                estimated_prompt_tokens, estimated_completion_tokens, model
            )

        return (
            response.choices[0].message.content
            or "I apologize, but I couldn't generate an answer at this time."
        )
