# Scholaria Project Root - Agent Knowledge Base

## Intent

MVP-완료된 학교 통합 RAG 시스템 - 문서 컨텍스트 기반 Q&A 플랫폼

## Constraints

- **TDD 필수**: Red → Green → Refactor 사이클 준수
- **코드 품질**: 커밋 전 ruff + mypy 통과 필수
- **테스트 구조**: `/tests/` 디렉터리 사용, 병렬 실행 안전성 보장
- **컨테이너화**: 모든 서비스 Docker 컨테이너 필수
- **PostgreSQL**: JSONField, 전문 검색 지원
- **Python 3.13+**: uv 패키지 매니저 사용

## Context

### 아키텍처 (Production Ready)
- **Backend**: FastAPI + SQLAlchemy + AsyncOpenAI services
- **Vector DB**: Qdrant (임베딩 검색)
- **Storage**: 파일 업로드 → 파싱 → 청킹 → 폐기 워크플로우 (MinIO 의존성 제거)
- **Cache**: Redis (Celery 백엔드)
- **Database**: PostgreSQL (메인 데이터)
- **AI**: OpenAI GPT + 임베딩, BGE Reranker

### 핵심 워크플로우
```bash
# 전체 품질 검사
uv run ruff check . && uv run ruff format . && uv run mypy . && uv run pytest

# 개발 서버 실행 (FastAPI + Refine)
uv run uvicorn backend.main:app --reload
cd frontend && pnpm dev

# Docker 서비스 시작 (dev overlay)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# 통합 테스트
uv run pytest
```

## Changelog

### 프로젝트 상태 (2025-09-30 기준)
- **MVP 완료**: 281개 테스트 통과, 모든 핵심 기능 구현 완료
- **프로덕션 준비**: Docker 배포, 보안 검증, 성능 최적화 완료
- **코드 품질**: ruff (2개 이슈), mypy 엄격 모드, pytest 병렬 실행

### 핵심 구현사항
- **데이터 모델**: Topic ↔ Context (N:N), Context → ContextItem (1:N)
- **수집 파이프라인**: Celery 백그라운드 작업으로 PDF/Markdown/FAQ 처리
  - PDF: Docling 파서 → 업로드 → 파싱 → 청킹 → 파일 폐기
  - FAQ: 2단계 생성 프로세스 (Context 생성 → Q&A 쌍 추가)
  - Markdown: 직접 편집 → 섹션별 스마트 청킹
- **검색 엔진**: 완전한 RAG 파이프라인 (임베딩 → 벡터 검색 → 리랭킹 → LLM)
- **API**: REST 엔드포인트, OpenAPI 문서화, 속도 제한
- **관리 인터페이스**: Refine 기반 관리자 UI (JWT 인증, bulk operations, 타입별 워크플로우)
- **웹 UI**: 토픽 선택, Q&A 인터페이스, 질문 히스토리

### 아키텍처 개선사항
- **Context-Topic 관계**: 1:N → N:N 변경으로 유연성 확보
- **파일 스토리지**: MinIO 의존성 제거, 임시 파일 처리 워크플로우
- **관리 워크플로우**: 타입별 Context 생성 양식, 청크 통계 표시
- **데이터베이스**: original_content, chunk_count, processing_status 필드 추가
- **라이브러리 마이그레이션**: Unstructured → Docling으로 PDF 파싱 개선

### FastAPI 운영 메모 (2025-10-01)
- SQLAlchemy 모델이 PostgreSQL 스키마를 직접 관리하며 Alembic이 이관 후 마이그레이션을 담당.
- `backend/services/rag_service.AsyncRAGService`는 Redis 캐시와 Qdrant를 사용하며 모든 의존성은 FastAPI 설정(`backend.config.Settings`)에서 로드.
- 테스트는 기본적으로 `uv run pytest backend/tests -q` 명령으로 실행하며, pytest 픽스처가 워커별 SQLite 파일을 자동 부트스트랩한다. Postgres 연동이 필요한 시나리오에서는 `docker-compose.dev.yml` 오버레이로 데이터베이스를 기동한다.
- 개별 테스트 모듈에서 FastAPI `get_db` 의존성을 다시 오버라이드하면 공용 스키마가 손상되므로 반드시 `backend/tests/conftest.py` 제공 픽스처를 사용한다.
- 개발 Docker Compose는 FastAPI 단일 서비스(`backend`)를 기동하며 Django 컨테이너는 제거됨.
- 데이터베이스 비밀번호는 반드시 환경 변수로 지정해야 하며, 설정에서 기본값을 제공하지 않는다. 미지정 시 URL은 비밀번호 없이 구성된다.
- 관리자 UI는 `frontend/` (Refine) 프로젝트로 제공되며 JWT 토큰을 localStorage에 저장해 API 요청에 첨부.

### Pydantic 스키마 패턴 (2025-10-01, updated 2025-10-08)
- 모든 스키마는 `backend/schemas/` 디렉터리에 모듈별로 분리 (`admin.py`, `context.py`, `topic.py`, `history.py`, `rag.py`, `utils.py`)
- **ORM 매핑**: 모든 `*Out` 스키마는 `ConfigDict(from_attributes=True)` 사용 (SQLAlchemy → Pydantic 자동 변환)
- **Datetime 직렬화**: `@field_serializer` + `backend.schemas.utils.to_local_iso()`로 timezone-aware ISO 8601 형식 변환
  - 적용 완료: `ContextOut`, `ContextItemOut`, `TopicOut`, `QuestionHistoryOut`, `AdminTopicOut`, `AdminContextOut`
- **Field 검증**: `Field(...)` 제약으로 입력 검증 (`min_length`, `max_length`, `gt`, `default_factory`)
- **Alias 패턴**: `Field(alias=...)` + `ConfigDict(populate_by_name=True)` (현재 `QuestionHistoryOut.topic` 사용)
- **Base 스키마**: 공통 필드는 `*Base` 클래스로 재사용 (`ContextBase`, `TopicBase`)
- **상세 문서**: `backend/schemas/README.md` 참고

### Django 의존성 제거 (2025-10-01)
- `backend/services/rag_service.py`에서 `asgiref.sync_to_async` 사용을 Python 표준 라이브러리 `asyncio.to_thread()`로 전환하여 Django 잔재물 완전 제거.
- 전환 대상: 임베딩 생성, Qdrant 검색, 리랭킹 처리 (총 4개소)
- 결과: 86/86 테스트 통과, ruff/mypy 검증 완료, 외부 의존성 없는 FastAPI native async 패턴 적용.
- 코드베이스에 Django 관련 import, 환경변수, 설정 없음 확인 완료.

### RAG 엔드포인트 테스트 복원 (2025-10-01)
- `backend/tests/test_rag_endpoint.py` 재활성화 - Django ORM 의존성을 SQLAlchemy mock으로 전환.
- 6개 테스트 케이스 추가: 정상 요청/응답, Pydantic 검증 (빈 질문, 잘못된 topic_id), 예외 처리 (ValueError, ConnectionError, Exception).
- 테스트 커버리지: 86 → 92 (+6), AsyncRAGService 전체를 mock하여 외부 의존성 차단.
- Mock 전략으로 단위 테스트 수준 유지, 통합 테스트는 별도 관리.

### Redis 공유 캐시 (2025-10-01)
- **임베딩 캐시**: 파일 기반 → Redis 전환으로 수평 확장 지원
  - 키 포맷: `embedding_cache:{namespace}:{sha256(model::text)}`
  - TTL: 30일 (설정 가능, `REDIS_EMBEDDING_CACHE_TTL_DAYS`)
  - Graceful fallback: Redis 연결 실패 시 자동으로 캐시 비활성화
- **Redis 설정**: AOF persistence + `allkeys-lru` eviction policy
- **테스트 전략**: 유닛 테스트 (mock) + 통합 테스트 (Redis 컨테이너), 122 tests pass
- **마이그레이션**: 기존 파일 캐시 (`storage/llamaindex_cache/`) 사용 중단, 설정 시 deprecation 경고
- **성능**: 여러 FastAPI/Celery 워커 간 캐시 공유로 OpenAI API 호출 감소 (캐시 적중 시)

### 프로덕션 기능
- **모니터링**: 헬스 체크 엔드포인트, 구조화된 로깅, 성능 메트릭
- **보안**: 파일 업로드 검증, 매직 바이트 체크, 크기 제한
- **배포**: Docker Compose, 환경 변수 관리, 백업 전략
- **CI/CD**: GitHub Actions, 코드 품질 검사, 보안 스캔
