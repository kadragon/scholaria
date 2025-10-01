# Task Summary: Redis Shared Cache

## Goal
Replace file-based `EmbeddingCache` with Redis-backed shared cache for horizontal scaling support.

## Key Changes
- **backend/retrieval/cache.py**: Rewrote `EmbeddingCache` to use sync Redis client
  - Removed `SimpleKVStore` dependency
  - Added connection retry with graceful fallback
  - Key format: `embedding_cache:{namespace}:{sha256(model::text)}`
  - TTL: 30 days (configurable)
- **backend/config.py**: Added `REDIS_EMBEDDING_CACHE_*` settings
  - `ENABLED` (default: True), `TTL_DAYS` (default: 30), `PREFIX` (default: "embedding_cache")
  - Deprecated `LLAMAINDEX_CACHE_*` settings with warning
- **backend/tests/test_embedding_cache.py**: 9 comprehensive tests (unit + integration)
  - Unit: mock-based, no Redis container (5 tests)
  - Integration: real Redis container (4 tests)
- **backend/tests/conftest.py**: Added `redis_client` fixture with auto-skip if unavailable
- **docker-compose.yml**: Redis persistence + eviction policy
  - AOF enabled, `allkeys-lru` policy

## Tests
- 122/122 tests pass (9 new cache tests)
- ruff clean, mypy clean
- Coverage: unit (mock) + integration (Redis container)

## Migration
- No action required for deployment
- Old file cache becomes orphaned (can be deleted)
- Graceful fallback if Redis unavailable

## Commits
- [Structural] Add Redis cache config and fixtures
- [Behavioral] Implement Redis-backed EmbeddingCache
- [Structural] Update Docker Redis config for production
