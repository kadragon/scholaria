# Progress: Redis Shared Cache Implementation

## Summary
✅ **완료** - Redis 기반 공유 캐시로 전환 완료, 수평 확장 지원 가능.

## Goal & Approach
파일 기반 `EmbeddingCache`를 Redis로 교체하여 여러 FastAPI/Celery 워커 간 임베딩 캐시 공유 지원. Sync Redis 클라이언트 사용, graceful fallback 구현.

## Completed Steps
1. ✅ **Test fixtures**: 9개 테스트 (unit 5개, integration 4개) + redis_client fixture
2. ✅ **Config update**: `REDIS_EMBEDDING_CACHE_*` 설정 추가, 기존 설정 deprecation
3. ✅ **Core implementation**: `EmbeddingCache` Redis 재구현 (get/set with TTL, connection error handling)
4. ✅ **Integration verification**: 122/122 테스트 통과
5. ✅ **Docker config**: Redis AOF persistence + allkeys-lru eviction
6. ✅ **Documentation**: AGENTS.md 업데이트, TASK_SUMMARY 작성

## Current Failures
None - all tests passing.

## Decision Log
- **Redis client choice**: Sync `redis.Redis` (not async) - `EmbeddingService` is synchronous
- **TTL strategy**: 30-day default TTL to handle model upgrades
- **Namespace**: `embedding_cache:{namespace}:{hash}` key format
- **Fallback**: Connection failure → disabled mode (no exceptions)
- **Key compatibility**: Kept sha256 hash format from old implementation
- **Test strategy**: Mock for unit tests, real Redis container for integration

## Next Step
Task complete. Ready to commit.
