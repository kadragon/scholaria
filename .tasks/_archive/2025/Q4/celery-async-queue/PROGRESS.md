# Progress: Celery Async Queue Integration

## Summary
Celery + Redis 기반 비동기 작업 큐를 도입하여 임베딩 재생성 등 장기 작업의 HTTP 차단 제거.

## Goal & Approach
- **Goal**: `bulk_regenerate_embeddings` 엔드포인트를 동기에서 비동기로 전환하여 타임아웃 제거 및 수평 확장 가능.
- **Approach**: TDD (Red→Green→Refactor) 단계별 진행; Celery 앱 → Config → Task → Endpoint → Docker.

## Completed Steps
1. **Step 1: Celery app init** ✅
   - `backend/celery_app.py` 생성 (Redis broker/backend, 타임아웃 30분)
   - `backend/tests/test_celery_app.py` (2 tests passing)
2. **Step 3: Celery task definition** ✅
   - `backend/tasks/embeddings.py` → `regenerate_embedding_task` (max_retries=3, exponential backoff)
   - `backend/tests/test_celery_tasks.py` (3 tests: success, retry, max retries)
3. **Step 4: Endpoint refactor** ✅
   - `backend/routers/admin/bulk_operations.py:68-110` → 동기 루프 제거, Celery 태스크 디스패치
   - `task_ids` 실제 Celery Task ID 배열 반환
   - All bulk ops tests passing (10 tests)
4. **Step 5: Docker worker setup** ✅
   - `docker-compose.yml` → `celery-worker` 서비스 추가 (postgres/redis/qdrant depends_on)

## Current Failures
_(none)_

## Decision Log
1. **Celery broker**: Redis 사용 (이미 Docker Compose에 존재).
2. **Result backend**: Redis (broker와 동일; 향후 DB로 변경 가능).
3. **Retry policy**: 최대 3회, exponential backoff (OpenAI API 일시적 장애 대응).
4. **Config**: `settings.redis_url` 재사용 (Step 2 스킵).
5. **DB Session**: `backend.models.base.Session()` context manager 사용 (Celery 태스크 내).
6. **Task timeout**: 30분 hard limit, 25분 soft limit (대량 임베딩 재생성 대비).

## Next Step
Celery 워커 실제 기동 테스트 (optional) → 프로덕션 배포 후 모니터링 권장 (Flower 등).
