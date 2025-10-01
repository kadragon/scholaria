# Research: Celery Async Queue Integration

## Goal
비동기 작업 큐(Celery + Redis)를 재도입하여 임베딩 재생성 등 장기 실행 작업이 HTTP 요청을 차단하지 않도록 개선.

## Scope
- `bulk_regenerate_embeddings` 엔드포인트 (현재 동기 실행, 대량 작업 시 타임아웃 위험)
- `generate_context_item_embedding` 함수 (OpenAI API 호출 포함)
- 향후 확장: PDF 파싱, 대량 인제스션, 스케줄 작업

## Related Files & Flows

### 1. Sync blocking code
- **`backend/routers/admin/bulk_operations.py:68-110`** → `bulk_regenerate_embeddings`
  - 동기 루프로 각 ContextItem에 대해 `generate_context_item_embedding` 호출
  - 실패 시 즉시 500 에러 반환, 부분 성공 롤백 없음
- **`backend/services/ingestion.py:154-224`** → `generate_context_item_embedding`
  - OpenAI embedding API 호출 + Qdrant 저장
  - 단일 아이템 처리 시간 ~200-500ms (API 레이턴시)

### 2. Infrastructure
- **`backend/config.py:29-31,54-56`** → Redis 설정 이미 존재 (`REDIS_HOST/PORT/DB`, `redis_url` property)
- **`pyproject.toml:20-21`** → `celery>=5.3.0`, `redis[hiredis]>=5.0.0` 이미 설치됨
- **`docker-compose.yml`** → Redis 컨테이너 이미 실행 중 (의존성 확인 필요)

### 3. Processing status tracking
- **`backend/models/context.py`** → `Context.processing_status` 필드 존재 (`PENDING/COMPLETED/FAILED`)
- **`bulk_operations.py:88-90,107-108`** → 상태 업데이트 로직 이미 구현

## Hypotheses

**H1**: Celery 워커 도입 시 HTTP 응답 시간이 100ms 미만으로 단축 (작업 큐 대기열 등록만 수행).
**H2**: 대량 임베딩 재생성(100+ items) 시 타임아웃/메모리 이슈 해결.
**H3**: 작업 실패 시 재시도 정책(최대 3회)으로 일시적 API 장애 대응 가능.

## Evidence

1. **현재 구현 분석**:
   - `bulk_regenerate_embeddings`는 `processed_count` 반환하지만 실제로는 동기 완료 후 반환 (202 Accepted 의미 없음).
   - 예: 100 items × 300ms = 30초 → Nginx/uvicorn timeout 초과 가능.
2. **Dependencies 확인**:
   - Celery, Redis 이미 설치됨.
   - `pytest-celery` 패키지 존재 → 테스트 인프라 준비 완료.

## Assumptions

- **Redis**: 이미 로컬/Docker 환경에서 실행 중 (dependencies/redis.py 확인 필요).
- **Celery 설정**: `backend/celery_app.py` 생성 필요 (새 파일).
- **Monitoring**: Celery Flower 등 모니터링 도구는 향후 추가 (scope 외).

## Open Questions

1. **Qdrant 동시성**: 여러 Celery 워커가 동시에 Qdrant에 쓸 때 충돌 여부? (Qdrant 자체는 동시 쓰기 지원).
2. **DB 세션 관리**: Celery 태스크 내에서 `get_db()` 직접 호출 불가 → 세션 생성 패턴 필요.
3. **Rollback 전략**: 부분 실패 시 전체 롤백 vs. 개별 아이템 재시도?

## Risks

- **Migration risk**: 기존 동기 테스트가 실패할 수 있음 (모킹 필요).
- **Deployment**: Celery 워커 프로세스 추가 필요 (Docker Compose 수정).
- **Backward compat**: 기존 클라이언트가 즉시 결과를 기대할 경우 Breaking Change.

## Next

1. **Plan**: Celery 앱 구조 설계 (config, tasks, worker setup).
2. **TDD**: 비동기 태스크 테스트 작성 (pytest-celery fixtures).
3. **Implement**: `@shared_task` 데코레이터 적용 + 엔드포인트 수정 + Docker 설정 업데이트.
