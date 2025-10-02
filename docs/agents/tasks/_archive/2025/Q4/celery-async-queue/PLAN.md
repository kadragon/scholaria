# Plan: Celery Async Queue Integration

## Objective
동기 임베딩 재생성 작업을 Celery 비동기 큐로 마이그레이션하여 HTTP 타임아웃 제거 및 수평 확장 가능.

## Constraints
- **No breaking changes**: 기존 동기 엔드포인트 테스트는 모킹으로 유지.
- **Backward compat**: 응답 포맷 유지 (`queued_count`, `task_ids[]`).
- **TDD**: 각 단계마다 테스트 작성 → 구현 → 리팩터.

## Target Files & Changes

### 1. New files (create)
- **`backend/celery_app.py`** (Celery 앱 초기화)
- **`backend/tasks/embeddings.py`** (Celery 태스크 정의)
- **`backend/tests/test_celery_tasks.py`** (비동기 태스크 테스트)

### 2. Modify existing
- **`backend/routers/admin/bulk_operations.py:68-110`**
  - 동기 루프 제거 → Celery 태스크 디스패치로 교체.
  - `task_ids` 반환 (실제 Celery Task ID 배열).
- **`backend/services/ingestion.py:154-224`**
  - `generate_context_item_embedding` → 순수 함수로 유지 (Celery 태스크에서 호출).
- **`backend/config.py`** (설정 추가)
  - `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` 필드 추가.
- **`docker-compose.yml`** (워커 서비스 추가)
  - `celery-worker` 컨테이너 정의.
- **`backend/main.py`** (선택적: 헬스체크)
  - Celery 워커 상태 확인 엔드포인트 (optional, scope 외).

## Test/Validation Cases

### Unit Tests
1. **Celery 앱 초기화 테스트** (`test_celery_app.py`)
   - `celery_app` 객체 생성 확인.
   - Broker URL 설정 검증.
2. **비동기 태스크 테스트** (`test_celery_tasks.py`)
   - `regenerate_embedding_task.delay(context_item_id)` 호출 시 태스크 ID 반환.
   - 모킹된 DB 세션에서 임베딩 생성 성공/실패 케이스.
3. **재시도 정책 테스트**
   - OpenAI API 실패 시 최대 3회 재시도 확인 (모킹).

### Integration Tests
4. **`bulk_regenerate_embeddings` 엔드포인트 테스트** (기존 수정)
   - 엔드포인트 호출 → 202 Accepted 즉시 반환.
   - `queued_count == len(context_ids)`, `task_ids` 길이 검증.
   - Celery 태스크 실제 실행 여부는 모킹 (pytest-celery eager mode).

### Edge Cases
5. **Context not found** → 태스크 내에서 실패 로그 + status=FAILED 업데이트.
6. **Qdrant unavailable** → 재시도 후 최종 실패 시 status=FAILED.
7. **Empty context_ids** → 즉시 `queued_count=0` 반환.

## Steps (TDD)

### [ ] Step 1: Celery 앱 초기화
- Write: `backend/tests/test_celery_app.py` → `test_celery_app_creation`.
- Implement: `backend/celery_app.py` → broker/backend 설정.
- Validate: `uv run pytest backend/tests/test_celery_app.py`.

### [ ] Step 2: Config 확장
- Write: `backend/tests/test_config.py` → `test_celery_broker_url` 추가.
- Implement: `backend/config.py` → `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` 추가.
- Validate: `uv run pytest backend/tests/test_config.py`.

### [ ] Step 3: 임베딩 재생성 Celery 태스크
- Write: `backend/tests/test_celery_tasks.py` → `test_regenerate_embedding_task_success`, `test_regenerate_embedding_task_retry`.
- Implement: `backend/tasks/embeddings.py` → `@shared_task(bind=True, max_retries=3)`.
- Validate: `uv run pytest backend/tests/test_celery_tasks.py`.

### [ ] Step 4: 엔드포인트 수정
- Write: `backend/tests/admin/test_bulk_operations.py` 수정 → Celery 태스크 모킹.
- Implement: `bulk_regenerate_embeddings` → 동기 루프 제거, 태스크 디스패치.
- Validate: `uv run pytest backend/tests/admin/test_bulk_operations.py`.

### [ ] Step 5: Docker Compose 워커 추가
- Write: `scripts/test_docker_integration.sh` 수정 (Celery 워커 헬스체크 추가).
- Implement: `docker-compose.yml` → `celery-worker` 서비스 정의.
- Validate: `docker compose up -d && docker compose ps | grep celery-worker`.

### [ ] Step 6: End-to-End 통합 테스트
- Write: `backend/tests/test_bulk_regeneration_e2e.py` (optional, full flow).
- Implement: 실제 Redis + Celery 환경에서 태스크 실행 확인.
- Validate: `uv run pytest backend/tests/test_bulk_regeneration_e2e.py`.

## Rollback

1. **Step 1-3 실패 시**: 새 파일만 삭제 (`git clean -fd backend/tasks backend/tests/test_celery*.py`).
2. **Step 4 실패 시**: `bulk_operations.py` revert (`git checkout HEAD -- backend/routers/admin/bulk_operations.py`).
3. **Step 5 실패 시**: Docker Compose 변경 롤백 (`git checkout HEAD -- docker-compose.yml`).

## Review Hotspots

- **DB Session 관리**: Celery 태스크 내에서 `Session()` 생성 → `sessionmaker` 재사용 패턴 확인.
- **Qdrant concurrency**: 동시 쓰기 시 인덱스 충돌 가능성 검토 (Qdrant는 lock-free 지원).
- **Task ID 반환**: `AsyncResult.id` vs. `Task.request.id` 혼동 주의.

## Status

- [x] Step 1: Celery app init (2 tests passing)
- [x] Step 2: Config expansion (skipped - redis_url already exists)
- [x] Step 3: Celery task definition (3 tests passing)
- [x] Step 4: Endpoint refactor (10 tests passing, all bulk ops)
- [x] Step 5: Docker worker setup (docker-compose.yml updated)
- [ ] Step 6: E2E integration test (optional, deferred)
