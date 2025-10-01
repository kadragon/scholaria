"""Tests for Redis-backed EmbeddingCache."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestEmbeddingCacheUnit:
    """Unit tests without Redis container (mock-based)."""

    def test_cache_disabled_when_redis_unavailable(self) -> None:
        """Cache should disable gracefully when Redis connection fails."""
        with patch(
            "redis.Redis.ping", side_effect=ConnectionError("Redis unavailable")
        ):
            from backend.retrieval.cache import EmbeddingCache

            cache = EmbeddingCache()
            assert not cache.enabled()

    def test_key_generation_format(self) -> None:
        """Cache key should be sha256(model::text)."""
        import hashlib

        from backend.retrieval.cache import EmbeddingCache

        cache = EmbeddingCache()
        expected = hashlib.sha256(b"text-embedding-3-large::hello world").hexdigest()
        actual = cache._make_key("hello world", "text-embedding-3-large")
        assert actual == f"embedding_cache:scholaria-default:{expected}"

    def test_cache_get_returns_none_on_miss(self) -> None:
        """Cache.get() should return None when key doesn't exist."""
        mock_redis = MagicMock()
        mock_redis.get.return_value = None

        with patch("redis.Redis.from_url", return_value=mock_redis):
            from backend.retrieval.cache import EmbeddingCache

            cache = EmbeddingCache()
            result = cache.get("test text", "test-model")
            assert result is None

    def test_cache_get_returns_embedding_on_hit(self) -> None:
        """Cache.get() should return deserialized embedding on hit."""
        import json

        mock_redis = MagicMock()
        mock_redis.get.return_value = json.dumps([0.1, 0.2, 0.3])

        with patch("redis.Redis.from_url", return_value=mock_redis):
            from backend.retrieval.cache import EmbeddingCache

            cache = EmbeddingCache()
            result = cache.get("test text", "test-model")
            assert result == [0.1, 0.2, 0.3]

    def test_cache_set_with_ttl(self) -> None:
        """Cache.set() should use SETEX with configured TTL."""
        import json

        mock_redis = MagicMock()

        with patch("redis.Redis.from_url", return_value=mock_redis):
            from backend.retrieval.cache import EmbeddingCache

            cache = EmbeddingCache()
            cache.set("test text", "test-model", [0.1, 0.2, 0.3])

            # Verify SETEX called with TTL (30 days = 2592000 seconds)
            mock_redis.setex.assert_called_once()
            call_args = mock_redis.setex.call_args
            # Check positional args: setex(name, time, value)
            assert len(call_args[0]) == 3
            key, ttl, value = call_args[0]
            assert key.startswith("embedding_cache:")
            assert ttl == 2592000
            assert json.loads(value) == [0.1, 0.2, 0.3]


class TestEmbeddingCacheIntegration:
    """Integration tests with real Redis container."""

    @pytest.fixture
    def cache(self, redis_client):
        """Create EmbeddingCache with test Redis instance."""
        from backend.retrieval.cache import EmbeddingCache

        # Clear all embedding cache keys before each test
        pattern = "embedding_cache:*"
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)

        return EmbeddingCache()

    def test_cache_roundtrip(self, cache) -> None:
        """Embedding should persist across get/set operations."""
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        text = "test roundtrip"
        model = "test-model"

        # Cache miss
        assert cache.get(text, model) is None

        # Cache set
        cache.set(text, model, embedding)

        # Cache hit
        result = cache.get(text, model)
        assert result == embedding

    def test_cache_different_models_different_keys(self, cache) -> None:
        """Same text with different models should use different keys."""
        text = "same text"
        embedding_v1 = [0.1, 0.2, 0.3]
        embedding_v2 = [0.4, 0.5, 0.6]

        cache.set(text, "model-v1", embedding_v1)
        cache.set(text, "model-v2", embedding_v2)

        assert cache.get(text, "model-v1") == embedding_v1
        assert cache.get(text, "model-v2") == embedding_v2

    def test_cache_ttl_set_correctly(self, cache, redis_client) -> None:
        """Cache entries should have TTL set."""
        text = "test ttl"
        model = "test-model"
        cache.set(text, model, [0.1, 0.2])

        # Get the actual Redis key
        key = cache._make_key(text, model)
        ttl = redis_client.ttl(key)

        # TTL should be ~30 days (2592000 seconds), allow some margin
        assert 2591900 < ttl <= 2592000

    def test_cache_concurrent_access(self, cache) -> None:
        """Multiple workers can access cache without conflicts."""
        import concurrent.futures

        def worker(i: int) -> list[float] | None:
            text = f"concurrent test {i}"
            model = "test-model"
            embedding = [float(i), float(i + 1)]

            cache.set(text, model, embedding)
            return cache.get(text, model)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            results = [f.result() for f in futures]

        # All workers should successfully read their own writes
        for i, result in enumerate(results):
            assert result == [float(i), float(i + 1)]
