# Scholaria Project Root - Agent Knowledge Base

## Intent
MVP-완료된 학교 통합 RAG 시스템 – 문서 컨텍스트 기반 Q&A 플랫폼.

## Constraints
- **TDD 필수**: Red → Green → Refactor 사이클을 유지한다.
- **코드 품질**: 커밋 전 `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy .` 모두 통과해야 한다.
- **테스트 구조**: 모든 테스트는 `backend/tests/` 아래에서 관리하며 병렬 실행 시에도 데이터 경쟁이 없어야 한다.
- **컨테이너화**: 개발과 배포 모두 `docker compose` 기반 (`docker-compose.yml`, 프로덕션은 `docker-compose.prod.yml`).
- **데이터베이스**: PostgreSQL JSON 필드와 전문 검색을 활용하고 Alembic 마이그레이션을 최신 상태로 유지한다.
- **Python 3.13+**: uv 패키지 매니저를 기본으로 사용한다.

## Context

### 아키텍처 (2025-10-09)
- **Backend**: FastAPI + SQLAlchemy + Celery + AsyncOpenAI 클라이언트.
- **Vector DB**: Qdrant (임베딩 검색 전용).
- **Storage**: 업로드 → Docling 파싱 → 청킹 → 임시 파일 폐기 (외부 MinIO 의존성 제거).
- **Cache**: Redis (Celery 백엔드, 임베딩 캐시, RAG 쿼리 캐시).
- **Database**: PostgreSQL이 주 데이터 저장소를 담당.
- **AI**: OpenAI text-embedding-3-large + GPT-4o-mini + BGE reranker.
- **Frontend**: Refine 기반 관리자 UI (Vite dev server, port 5173).

### 핵심 워크플로우
```bash
# 의존성 설치
uv sync

# 품질 검사
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest backend/tests/

# 개발 서버
uv run uvicorn backend.main:app --reload --port 8001
(cd frontend && pnpm install && pnpm dev)

# Docker 개발 환경
docker compose up -d
docker compose exec backend alembic upgrade head

# 프로덕션 오케스트레이션
docker compose -f docker-compose.prod.yml up -d
```

## Changelog

### 프로젝트 상태 (2025-10-09)
- 201 tests passed, 5 skipped, 85% coverage (`uv run pytest --maxfail=1 --disable-warnings -q` 결과).
- `docker-compose.yml`: backend, postgres, redis, qdrant, frontend, celery-worker, flower 서비스 포함.
- `docker-compose.prod.yml`: nginx 리버스 프록시 + 백엔드 스택으로 프로덕션 배포 가능.
- uv.lock 기준 Docling 2.53.0, Python 3.13.5 환경 최신화 완료.

### 핵심 구현사항
- Topic↔Context N:N 모델, ContextItem 청크 메타데이터, Docling 기반 PDF/Markdown/FAQ 처리 파이프라인.
- RAG 파이프라인: 임베딩 → Qdrant 토픽 필터링 → BGE rerank → GPT-4o-mini 응답, Redis에 쿼리 결과 15분 캐시(빈 결과 5분).
- FastAPI REST API: OpenAPI, JWT 인증, 레이트 리밋 모니터링, Refine 관리자 UI 일체화.
- 관리자 UI: JWT 토큰을 localStorage에 저장, 벌크 작업 및 타입별 작성 플로우 지원.

### 아키텍처 개선사항
- Context-Topic 관계를 N:N으로 전환하여 토픽 재사용 유연성 확보.
- Docling 전환으로 외부 파서 서비스 제거, 모든 파일 처리는 in-process로 수행.
- Redis 공유 캐시: `backend/retrieval/cache.EmbeddingCache` TTL 30일, 장애 시 자동 비활성화.
- `backend/services/rag_service.AsyncRAGService`가 Redis에 쿼리 응답을 15분 캐시하고 빈 결과는 5분만 캐시한다.

### FastAPI 운영 메모 (2025-10-09)
- 설정은 `backend/config.Settings`에서 일관 관리하며 필수 환경 변수는 기본값을 제공하지 않는다.
- 기본 테스트 실행: `uv run pytest backend/tests -q`. PostgreSQL/Redis/Qdrant가 필요한 시나리오는 `docker compose up postgres redis qdrant` 후 실행.
- 개발 Docker Compose는 `scripts/docker/dev-entrypoint.sh`로 uv 환경을 확인하고 `uvicorn` 핫 리로드를 구동한다.
- 데이터베이스 비밀번호는 `.env` 또는 Compose 환경 변수로 지정해야 하며 기본 템플릿은 `postgres/postgres`.

### Alembic 마이그레이션 가이드 (2025-10-09)
- 생성: `uv run alembic revision -m "description"` (자동 생성 실패 시 수동 편집).
- 네이밍: `0001`, `0002` 형식의 숫자 프리픽스 + 선행 ID `down_revision`.
- 테스트: `backend/tests/test_alembic_migrations.py`에서 업/다운/멱등성 검증 추가·유지.
- 적용: 개발 환경은 `docker compose exec backend uv run alembic upgrade head`, 프로덕션은 `docker compose -f docker-compose.prod.yml exec backend ...`.

### Pydantic 스키마 패턴 (2025-10-08 유지)
- 스키마는 `backend/schemas/` 모듈별 분리, `ConfigDict(from_attributes=True)` 사용.
- `Field` 제약과 `backend.schemas.utils.to_local_iso()` serializer 재사용.
- Alias가 필요한 필드는 `populate_by_name=True`로 snake/camel 간 호환 유지.

### Django 의존성 제거 (2025-10-01)
- Django 잔재 import 제거, `asyncio.to_thread()` 기반 async 서비스로 전환 완료.

### RAG 엔드포인트 테스트 (2025-10-01 업데이트 유지)
- `backend/tests/test_rag_endpoint.py`, `backend/tests/test_rag_streaming.py`로 성공/검증/에러 플로우 커버.
- 외부 의존성은 Mock으로 차단하고 Docker Compose 기반 통합 테스트는 별도 관리.

### Redis 공유 캐시 (2025-10-01 → 2025-10-09 업데이트)
- 임베딩 캐시: `REDIS_EMBEDDING_CACHE_*` 설정, TTL 30일, 실패 시 graceful fallback.
- 쿼리 응답 캐시: Redis set + TTL 15분, 빈 결과 TTL 5분, 장애 시 캐시 비활성화 후 동작 지속.

### 프로덕션 기능
- 헬스 체크, 구조화 로깅, Flower 모니터링, 백업 전략 `docs/BACKUP_STRATEGY.md`.
- CI/CD: GitHub Actions에서 ruff/mypy/pytest/coverage 실행 (보안 스캔 TODO는 워크플로우에 기록).
