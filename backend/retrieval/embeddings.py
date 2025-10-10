from __future__ import annotations

from typing import TYPE_CHECKING

import openai

from backend.config import settings
from backend.observability import get_tracer

from .cache import EmbeddingCache
from .monitoring import OpenAIUsageMonitor

if TYPE_CHECKING:
    pass

tracer = get_tracer(__name__)


class EmbeddingService:
    """Service for generating embeddings using OpenAI API."""

    def __init__(self) -> None:
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL
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
        with tracer.start_as_current_span("rag.embedding") as span:
            if text is None or not text.strip():
                raise ValueError("Text cannot be None or empty")

            span.set_attribute("text.length", len(text))
            span.set_attribute("model.name", self.model)

            if self.cache.enabled():
                cached = self.cache.get(text, self.model)
                if cached is not None:
                    span.set_attribute("cache.hit", True)
                    return cached

            span.set_attribute("cache.hit", False)

            # Track request timing for rate limiting
            self.monitor.track_request_timestamp("embeddings")

            response = self.client.embeddings.create(model=self.model, input=text)
            embedding = response.data[0].embedding

            # Track usage metrics
            if hasattr(response, "usage") and response.usage:
                # Ensure we get integers rather than MagicMock objects in tests
                total_tokens = (
                    int(response.usage.total_tokens)
                    if hasattr(response.usage, "total_tokens")
                    else 0
                )
                span.set_attribute("tokens.total", total_tokens)
                self.monitor.track_embedding_usage(total_tokens, self.model)
            else:
                # Estimate tokens if usage not available (approximate 4 chars per token)
                estimated_tokens = len(text) // 4
                span.set_attribute("tokens.total", estimated_tokens)
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
        with tracer.start_as_current_span("rag.embedding.batch") as span:
            if not texts:
                raise ValueError("Texts list cannot be empty")

            span.set_attribute("batch.size", len(texts))
            span.set_attribute("model.name", self.model)

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

            cache_hits = len(texts) - len(texts_to_fetch)
            span.set_attribute("cache.hits", cache_hits)
            span.set_attribute("cache.misses", len(texts_to_fetch))

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
                    # Ensure we get integers rather than MagicMock objects in tests
                    total_tokens = (
                        int(response.usage.total_tokens)
                        if hasattr(response.usage, "total_tokens")
                        else 0
                    )
                    span.set_attribute("tokens.total", total_tokens)
                    self.monitor.track_embedding_usage(total_tokens, self.model)
                else:
                    # Estimate tokens if usage not available
                    estimated_tokens = sum(len(text) // 4 for text in texts_to_fetch)
                    span.set_attribute("tokens.total", estimated_tokens)
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
