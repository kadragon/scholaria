from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from openai import OpenAI

from .cache import EmbeddingCache
from .monitoring import OpenAIUsageMonitor

if TYPE_CHECKING:
    pass


class EmbeddingService:
    """Service for generating embeddings using OpenAI API."""

    def __init__(self) -> None:
        self.client = OpenAI(api_key=getattr(settings, "OPENAI_API_KEY", None))
        self.model = getattr(
            settings, "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
        )
        self.cache = EmbeddingCache()
        self.monitor = OpenAIUsageMonitor()

    def generate_embedding(self, text: str | None) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to generate embedding for

        Returns:
            List of float values representing the embedding

        Raises:
            ValueError: If text is None or empty
        """
        if text is None or not text.strip():
            raise ValueError("Text cannot be None or empty")

        if self.cache.enabled():
            cached = self.cache.get(text, self.model)
            if cached is not None:
                return cached

        # Track request timing for rate limiting
        self.monitor.track_request_timestamp("embeddings")

        response = self.client.embeddings.create(model=self.model, input=text)
        embedding = response.data[0].embedding

        # Track usage metrics
        if hasattr(response, "usage") and response.usage:
            self.monitor.track_embedding_usage(response.usage.total_tokens, self.model)
        else:
            # Estimate tokens if usage not available (approximate 4 chars per token)
            estimated_tokens = len(text) // 4
            self.monitor.track_embedding_usage(estimated_tokens, self.model)

        if self.cache.enabled():
            self.cache.set(text, self.model, embedding)

        return embedding

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts in a single API call.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors

        Raises:
            ValueError: If texts list is empty
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")

        cached_results: list[list[float] | None] = []
        texts_to_fetch: list[str] = []

        if self.cache.enabled():
            for text in texts:
                cached_results.append(self.cache.get(text, self.model))
                if cached_results[-1] is None:
                    texts_to_fetch.append(text)
        else:
            cached_results = [None for _ in texts]
            texts_to_fetch = texts

        fetched_embeddings: list[list[float]] = []
        if texts_to_fetch:
            # Track request timing for rate limiting
            self.monitor.track_request_timestamp("embeddings")

            response = self.client.embeddings.create(
                model=self.model, input=texts_to_fetch
            )
            fetched_embeddings = [item.embedding for item in response.data]

            # Track usage metrics
            if hasattr(response, "usage") and response.usage:
                self.monitor.track_embedding_usage(
                    response.usage.total_tokens, self.model
                )
            else:
                # Estimate tokens if usage not available
                estimated_tokens = sum(len(text) // 4 for text in texts_to_fetch)
                self.monitor.track_embedding_usage(estimated_tokens, self.model)

        # Merge cached and fetched results while persisting new entries
        result: list[list[float]] = []
        fetch_index = 0
        for idx, cached in enumerate(cached_results):
            if cached is not None:
                result.append(cached)
                continue

            embedding = fetched_embeddings[fetch_index]
            fetch_index += 1
            if self.cache.enabled():
                self.cache.set(texts[idx], self.model, embedding)
            result.append(embedding)

        return result
