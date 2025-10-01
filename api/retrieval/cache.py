"""LlamaIndex-backed caching utilities for retrieval workflows."""

from __future__ import annotations

import hashlib
from pathlib import Path

from django.conf import settings

try:
    from llama_index.core.storage.kvstore.simple_kvstore import SimpleKVStore
except Exception:  # pragma: no cover - optional dependency guard
    SimpleKVStore = None  # type: ignore[misc,assignment]


class EmbeddingCache:
    """Simple on-disk cache for embeddings using LlamaIndex storage primitives."""

    def __init__(self) -> None:
        self._enabled = bool(getattr(settings, "LLAMAINDEX_CACHE_ENABLED", False))
        self._persist_path: Path | None = None
        self._store: SimpleKVStore | None = None

        if self._enabled and SimpleKVStore is not None:
            cache_dir = Path(settings.LLAMAINDEX_CACHE_DIR)
            cache_dir.mkdir(parents=True, exist_ok=True)
            self._persist_path = cache_dir / "embedding_cache.json"

            if self._persist_path.exists():
                self._store = SimpleKVStore.from_persist_path(str(self._persist_path))
            else:
                self._store = SimpleKVStore()
        else:
            self._enabled = False  # Guard against missing dependency

    def _make_key(self, text: str, model: str) -> str:
        digest_source = f"{model}::{text}".encode()
        return hashlib.sha256(digest_source).hexdigest()

    def get(self, text: str, model: str) -> list[float] | None:
        if not self._enabled or not self._store:
            return None

        key = self._make_key(text, model)
        payload = self._store.get(key)
        if not payload:
            return None
        return payload.get("embedding")

    def set(self, text: str, model: str, embedding: list[float]) -> None:
        if not self._enabled or not self._store:
            return

        key = self._make_key(text, model)
        self._store.put(key, {"embedding": embedding})

        if self._persist_path:
            self._store.persist(str(self._persist_path))

    def enabled(self) -> bool:
        return self._enabled
