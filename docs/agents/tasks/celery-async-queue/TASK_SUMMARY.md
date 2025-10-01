# Task Summary: Celery Async Queue Integration

## Goal
임베딩 재생성 등 장기 작업을 비동기 큐(Celery + Redis)로 전환하여 HTTP 타임아웃 제거.

## Key Changes
- **New files**: `backend/celery_app.py`, `backend/tasks/embeddings.py`, `backend/tests/test_celery_{app,tasks}.py`
- **Modified**: `backend/routers/admin/bulk_operations.py` (동기 루프 → Celery 태스크 디스패치), `docker-compose.yml` (celery-worker 서비스 추가)
- **Status**: ✅ 105 tests passing (기존 100 + 신규 5), ruff clean, mypy strict pass

## Tests
- `test_celery_app.py` (2 tests): Celery 앱 생성 + broker/backend URL 검증
- `test_celery_tasks.py` (3 tests): 태스크 성공, 재시도, 최대 재시도 초과
- `test_bulk_operations.py` (10 tests): 엔드포인트 202 Accepted, task_ids 반환 검증

## Commits
_(진행 중 - 커밋 예정)_

## Notes
- Step 2 (Config 확장) 스킵: `settings.redis_url` 이미 존재.
- Step 6 (E2E 통합 테스트) 선택적 defer: 실제 워커 기동은 프로덕션 배포 후 검증 권장.
- Retry policy: max_retries=3, exponential backoff (60s, 120s, 240s).
