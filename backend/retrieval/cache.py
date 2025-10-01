"""Redis-backed caching utilities for retrieval workflows."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from backend.config import settings


class EmbeddingCache:
    """Redis-backed cache for embeddings with graceful fallback."""

    def __init__(self) -> None:
        self._enabled = False
        self._client: Any = None
        self._ttl_seconds: int = 0

        # Check for deprecated file-based cache config
        if settings.LLAMAINDEX_CACHE_ENABLED:
            import warnings

            warnings.warn(
                "LLAMAINDEX_CACHE_* settings are deprecated. Use REDIS_EMBEDDING_CACHE_* instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        # Initialize Redis cache
        if settings.REDIS_EMBEDDING_CACHE_ENABLED:
            try:
                import redis

                self._client = redis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2,
                )
                # Test connection
                self._client.ping()
                self._enabled = True
                self._ttl_seconds = settings.REDIS_EMBEDDING_CACHE_TTL_DAYS * 86400
            except Exception:
                # Graceful fallback - disable cache on any connection error
                self._enabled = False
                self._client = None

    def _make_key(self, text: str, model: str) -> str:
        digest_source = f"{model}::{text}".encode()
        hash_digest = hashlib.sha256(digest_source).hexdigest()
        namespace = settings.LLAMAINDEX_CACHE_NAMESPACE
        prefix = settings.REDIS_EMBEDDING_CACHE_PREFIX
        return f"{prefix}:{namespace}:{hash_digest}"

    def get(self, text: str, model: str) -> list[float] | None:
        if not self._enabled or not self._client:
            return None

        try:
            key = self._make_key(text, model)
            cached = self._client.get(key)
            if not cached:
                return None

            return json.loads(cached)
        except Exception:
            # Graceful degradation on any error
            return None

    def set(self, text: str, model: str, embedding: list[float]) -> None:
        if not self._enabled or not self._client:
            return

        try:
            key = self._make_key(text, model)
            value = json.dumps(embedding)
            self._client.setex(key, self._ttl_seconds, value)
        except Exception:
            # Graceful degradation - don't raise on cache write failure
            pass

    def enabled(self) -> bool:
        return self._enabled
