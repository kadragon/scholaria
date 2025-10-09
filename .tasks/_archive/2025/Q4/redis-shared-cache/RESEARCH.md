# Research: Redis Shared Cache for Horizontal Scaling

## Goal
Replace file-based `EmbeddingCache` with Redis-backed shared cache to enable horizontal scaling across multiple FastAPI instances.

## Scope
- Embedding cache persistence layer
- Cache invalidation strategy
- Connection pooling & retry logic
- Testing strategy for distributed cache scenarios

## Related Files & Flows

### Current State
- **`backend/retrieval/cache.py`**: File-based `EmbeddingCache` using LlamaIndex `SimpleKVStore`
  - Persists to `storage/llamaindex_cache/{namespace}_embedding_cache.json`
  - Keys: `sha256(f"{model}::{text}")`
  - Single-process only, no shared state
- **`backend/retrieval/embeddings.py`**: `EmbeddingService` uses `EmbeddingCache` directly
  - Synchronous cache get/set during embedding generation
  - Used in both single (`generate_embedding`) and batch (`generate_embeddings_batch`) flows
- **`backend/services/rag_service.py`**: `AsyncRAGService` has separate Redis-based query cache (15-min TTL)
  - Keys: `rag_query:{md5(query+topic_ids+params)}`
  - Uses `redis.asyncio` client
- **`backend/dependencies/redis.py`**: Async Redis client dependency
  - Connection from `settings.redis_url`
  - Auto-close on teardown
- **`backend/celery_app.py`**: Celery uses Redis as broker & backend
  - Same Redis instance (`settings.redis_url`)

### Integration Points
1. **Embedding generation** (sync context):
   - `EmbeddingService.generate_embedding()` → OpenAI API → cache.set()
   - Called from Celery tasks (`backend/tasks/embeddings.py`)
   - Called from RAG query pipeline (via `asyncio.to_thread()`)
2. **Batch embeddings** (sync context):
   - Used during context ingestion (bulk processing)
   - Cache hit rate critical for performance

## Hypotheses

### H1: Redis can replace file-based cache with minimal latency overhead
- **Evidence**: `AsyncRAGService` already uses Redis for query cache with 15-min TTL
- **Assumption**: Network latency to Redis << OpenAI API latency (50ms vs 500ms+)
- **Risk**: Thundering herd on cache miss → rate limit protection already exists in `OpenAIUsageMonitor`

### H2: Async Redis client can be used in sync context via `asyncio.run()`
- **Evidence**: `EmbeddingService` is synchronous, called from both sync and async contexts
- **Alternative**: Use `redis` (sync) client instead of `redis.asyncio`
- **Trade-off**: Mixing sync/async clients vs single async client with bridge

### H3: Shared cache improves performance in multi-worker setup
- **Evidence**: Celery workers and FastAPI instances share embedding workload
- **Assumption**: Cache hit rate > 30% for typical queries (verification needed after deployment)
- **Measurement**: Compare pre/post cache hit rates via monitoring

## Evidence

### Current Cache Configuration
```python
# backend/config.py
LLAMAINDEX_CACHE_ENABLED: bool = Field(default=False)  # ⚠️ Disabled by default
LLAMAINDEX_CACHE_DIR: str = Field(default="storage/llamaindex_cache")
LLAMAINDEX_CACHE_NAMESPACE: str = Field(default="scholaria-default")
```

### Redis Already Available
- Docker Compose: `redis:7-alpine` container
- Used by: Celery broker/backend, RAG query cache
- No connection pooling configured (uses default `from_url()`)

### Cache Key Format
```python
# Current: backend/retrieval/cache.py:31
def _make_key(self, text: str, model: str) -> str:
    digest_source = f"{model}::{text}".encode()
    return hashlib.sha256(digest_source).hexdigest()
```

## Assumptions & Open Questions

### Assumptions
1. Redis instance has sufficient memory for embedding cache (embeddings are ~12KB each for 3072-dim)
2. Redis persistence (RDB/AOF) is configured in production (not verified in current docker-compose.yml)
3. Cache invalidation is unnecessary (embeddings are deterministic per model version)

### Open Questions
1. **TTL strategy**: Should embedding cache expire? (current file cache never expires)
   - Proposal: 30-day TTL to handle model upgrades
2. **Namespace conflicts**: Use same Redis DB (0) or separate DB for cache?
   - Current: Celery uses DB 0, RAG query cache uses DB 0
   - Proposal: Keep DB 0, use key prefix `embedding_cache:{namespace}:{hash}`
3. **Sync vs Async client**:
   - Option A: Use `redis` (sync) in `EmbeddingService`, keep `redis.asyncio` in `AsyncRAGService`
   - Option B: Use single `redis.asyncio` client + `asyncio.run()` in sync contexts
   - **Decision needed**: Test both approaches for latency/complexity trade-offs

## Risks

### High
- **Breaking change**: Existing file-based caches become orphaned (one-time migration cost)
- **Network dependency**: Redis downtime blocks all embedding operations
  - Mitigation: Implement fallback to no-cache mode on Redis failure

### Medium
- **Memory pressure**: Unbounded cache growth if TTL not set
  - Mitigation: Set 30-day TTL + `maxmemory-policy allkeys-lru` in Redis config
- **Connection exhaustion**: Multiple workers sharing Redis without pooling
  - Mitigation: Configure `connection_pool_kwargs` with `max_connections` limit

### Low
- **Key collision**: SHA256 hash collision (negligible probability)
- **Performance regression**: Redis latency > file I/O latency
  - Measurement: Benchmark with production workload after deployment

## Next Steps
1. **Design decision**: Sync vs async Redis client approach
2. **Plan implementation**: Update `EmbeddingCache` class interface
3. **Test strategy**: Unit tests + integration tests with Redis container
4. **Migration guide**: Document cache transition for deployment
