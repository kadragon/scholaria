# Plan: Redis Shared Cache Implementation

## Objective
Replace file-based `EmbeddingCache` with Redis-backed implementation for horizontal scaling support.

## Constraints
- **Backwards compatibility**: Must support graceful fallback when Redis unavailable
- **Zero downtime**: Existing file cache becomes read-only (no migration needed)
- **Performance**: Redis latency must be < 50ms for cache operations
- **TDD**: All changes must be test-first

## Target Files & Changes

### Core Implementation
1. **`backend/retrieval/cache.py`** - Replace `EmbeddingCache` implementation
   - Remove `SimpleKVStore` dependency
   - Add sync Redis client (`redis.Redis`, not async)
   - Keep same interface: `get()`, `set()`, `enabled()`, `_make_key()`
   - Add connection retry logic with fallback to disabled mode

2. **`backend/config.py`** - Add Redis cache configuration
   - Add `REDIS_EMBEDDING_CACHE_ENABLED: bool` (default: `True`)
   - Add `REDIS_EMBEDDING_CACHE_TTL_DAYS: int` (default: `30`)
   - Add `REDIS_EMBEDDING_CACHE_PREFIX: str` (default: `"embedding_cache"`)
   - Keep `LLAMAINDEX_CACHE_*` for backwards compatibility warning

### Testing
3. **`backend/tests/test_embedding_cache.py`** - New comprehensive test suite
   - Test Redis cache hit/miss scenarios
   - Test connection failure fallback
   - Test TTL expiration
   - Test key generation consistency
   - Test concurrent access (multi-worker simulation)

4. **`backend/tests/conftest.py`** - Add Redis test fixture
   - Add `redis_client` fixture with cleanup
   - Add `mock_redis` fixture for unit tests without container

### Integration
5. **`backend/retrieval/embeddings.py`** - No changes needed (interface unchanged)
6. **`docker-compose.yml`** - Redis config validation
   - Verify Redis persistence enabled (RDB + AOF)
   - Add `maxmemory-policy allkeys-lru`

## Test/Validation Cases

### Unit Tests (No Redis container)
1. ✅ Cache disabled when Redis connection fails
2. ✅ Key generation matches old format (`sha256(model::text)`)
3. ✅ TTL set correctly on cache.set()
4. ✅ Graceful degradation when Redis unavailable

### Integration Tests (With Redis container)
5. ✅ Cache hit returns correct embedding
6. ✅ Cache miss returns None
7. ✅ Cache set persists across connections
8. ✅ TTL expiration after configured duration
9. ✅ Concurrent get/set from multiple workers

### Backward Compatibility Tests
10. ✅ Old file cache config (`LLAMAINDEX_CACHE_*`) logs deprecation warning
11. ✅ System works when both file and Redis cache disabled

## Implementation Steps

### Step 1: Add test fixtures (TDD foundation)
- [x] Create `backend/tests/test_embedding_cache.py` with failing tests
- [x] Add `redis_client` fixture to `conftest.py`
- [x] Add `mock_redis` fixture for unit tests
- **Status**: ✅ Complete - 7 failing tests, 2 passing (graceful degradation works)

### Step 2: Update config (preparation)
- [x] Add Redis cache settings to `backend/config.py`
- [x] Add deprecation warning for `LLAMAINDEX_CACHE_*` if enabled
- **Status**: ✅ Complete - Config ready

### Step 3: Implement RedisEmbeddingCache (core logic)
- [x] Rewrite `EmbeddingCache.__init__()` to use sync Redis client
- [x] Implement `get()` with Redis `GET` command
- [x] Implement `set()` with Redis `SETEX` (TTL support)
- [x] Add connection error handling with disabled fallback
- [x] Update `_make_key()` to use namespace prefix
- **Status**: ✅ Complete - 9/9 tests pass

### Step 4: Integration verification
- [x] Run full test suite (`uv run pytest`)
- [x] Verify `test_rag_endpoint.py` still passes (uses mock, unaffected)
- [x] Verify `test_celery_tasks.py` passes with real Redis
- **Status**: ✅ Complete - 122/122 tests pass

### Step 5: Docker config update
- [x] Add Redis persistence config to `docker-compose.yml`
- [x] Add `maxmemory-policy` configuration
- [x] Test with `docker compose up --build`
- **Status**: ✅ Complete - AOF + LRU eviction enabled

### Step 6: Documentation
- [x] Update `docs/agents/AGENTS.md` with Redis cache decision
- [x] Add cache monitoring guidance (Redis `INFO` stats)
- [x] Document migration path (file cache → Redis cache)
- **Status**: ✅ Complete (file cache → Redis cache)

## Rollback Plan
1. Set `REDIS_EMBEDDING_CACHE_ENABLED=False` in environment
2. System falls back to no-cache mode (OpenAI API direct calls)
3. No code rollback needed (graceful degradation built-in)

## Review Hotspots
- **`backend/retrieval/cache.py:__init__()`**: Connection error handling must not raise exceptions
- **`backend/retrieval/cache.py:set()`**: TTL must be applied (use `SETEX`, not `SET` + `EXPIRE`)
- **`backend/tests/test_embedding_cache.py`**: Must test both unit (mock) and integration (container) scenarios
- **Redis config**: `maxmemory-policy` must be set to prevent OOM

## Status
- [ ] Step 1: Test fixtures (TDD foundation)
- [ ] Step 2: Config update
- [ ] Step 3: Core implementation
- [ ] Step 4: Integration verification
- [ ] Step 5: Docker config
- [ ] Step 6: Documentation
