# Plan: Django 제거 및 프로젝트 구조 리팩토링

## Objective
Django 레거시 코드를 완전히 제거하고 FastAPI 중심의 깔끔한 모노레포 구조로 전환

## Constraints
- **무중단**: 기존 FastAPI 서비스 동작 유지
- **테스트 우선**: 각 단계마다 테스트 통과 확인
- **Docker 호환**: Docker Compose 프로덕션 빌드 정상 동작
- **문서 동기화**: README, DEPLOYMENT, ARCHITECTURE 업데이트

## Target Files & Changes

### Step 1: Celery 작업을 FastAPI 서비스로 이동
**Files**:
- `rag/tasks.py` (499 lines) → `api/services/ingestion.py` (new)
- `api/routers/contexts.py` (255 lines) → update to use `ingestion.py`
- `api/routers/admin/bulk_operations.py` → remove `core.celery` import

**Changes**:
- `@shared_task` → regular async/sync functions
- Django ORM (`Context.objects`) → SQLAlchemy (`db.query(Context)`)
- Celery `.delay()` → direct function call (현재 FastAPI는 동기 처리)

**Tests**:
- `api/tests/test_ingestion_service.py` (new): PDF/Markdown/FAQ ingestion
- `api/tests/test_contexts.py`: 기존 테스트 유지 (16/16)

### Step 2: Django 코드 제거
**Files** (제거):
- `core/` (전체 폴더)
- `rag/` (전체 폴더)
- `manage.py`
- `templates/` (전체 폴더)
- `static/`, `staticfiles/`
- Django 의존성 from `pyproject.toml`

**Changes**:
- `pyproject.toml`: Django, django-celery-beat, drf-spectacular 제거
- 유지: SQLAlchemy, Alembic, FastAPI, Celery (백그라운드 작업용, Django 의존성 제거 버전)

**Validation**:
- `uv run python -c "import django"` → ImportError 확인

### Step 3: 폴더 구조 재구성 (모노레포)
**Before**:
```
scholaria/
├── api/
├── admin-frontend/
├── core/          (Django)
├── rag/           (Django)
├── alembic/
└── ...
```

**After**:
```
scholaria/
├── backend/       (← api/)
├── frontend/      (← admin-frontend/)
├── alembic/
├── nginx/
├── scripts/
├── docs/
└── ...
```

**Changes**:
- `git mv api backend`
- `git mv admin-frontend frontend`
- Update imports: `from api.routers` → `from backend.routers`
- Update `alembic/env.py`: `from api.models` → `from backend.models`

**Validation**:
- `uv run python -c "from backend.main import app"`
- `cd frontend && npm run build`

### Step 4: Docker 구성 업데이트
**Files**:
- `docker-compose.prod.yml`: `web`, `celery-worker`, `celery-beat` 서비스 제거
- `Dockerfile.prod` → `Dockerfile.backend`
- `Dockerfile.admin` → `Dockerfile.frontend`

**Changes**:
- `docker-compose.prod.yml`:
  - 제거: `web`, `celery-worker`, `celery-beat` (Django)
  - 유지: `fastapi`, `admin-frontend`, `postgres`, `redis`, `qdrant`, `nginx`
  - `fastapi.build.context: ./backend`
  - `admin-frontend.build.context: ./frontend`
- `Dockerfile.backend`:
  - `COPY backend/ /app/backend/`
  - `WORKDIR /app`
  - `CMD uvicorn backend.main:app --host 0.0.0.0 --port 8001`
- `Dockerfile.frontend`:
  - `COPY frontend/ /app/frontend/`
  - `WORKDIR /app/frontend`

**Validation**:
- `docker-compose -f docker-compose.prod.yml build`
- `docker-compose -f docker-compose.prod.yml up -d`
- Health checks: `/health`, `/api/topics`

### Step 5: Nginx 설정 업데이트
**Files**:
- `nginx/nginx.conf`

**Changes**:
- 제거: `/admin/` → Django admin 프록시
- 유지: `/api/` → FastAPI, `/admin/` → Refine Admin (frontend)

**Validation**:
- `curl http://localhost/api/topics`
- `curl http://localhost/admin/` (Refine Admin)

### Step 6: 비즈니스 로직 테스트 이동
**Files** (Django → FastAPI):
- `rag/tests/test_ingestion.py` → `backend/tests/test_ingestion_service.py`
- `rag/tests/test_retrieval.py` → `backend/tests/test_rag_service.py` (already exists)
- `rag/tests/golden_dataset.py` → `backend/tests/golden_dataset.py`
- `rag/tests/performance_benchmarks.py` → `backend/tests/performance_benchmarks.py`

**Changes**:
- Django TestCase → pytest fixtures
- Django ORM → SQLAlchemy
- `self.assertEqual` → `assert`

**Validation**:
- `uv run pytest backend/tests/` (목표: 100+ tests)

### Step 7: 문서 업데이트
**Files**:
- `README.md`
- `docs/DEPLOYMENT.md`
- `docs/ARCHITECTURE_DECISIONS.md`
- `docs/agents/AGENTS.md` (core, rag 폴더 제거 반영)

**Changes**:
- README: 폴더 구조 섹션 업데이트 (backend/, frontend/)
- DEPLOYMENT: Docker 서비스 목록 업데이트 (Django 제거)
- ARCHITECTURE: Django → FastAPI 전환 완료 기록

**Validation**:
- 문서 링크 체크: `grep -r "api/" docs/` → `backend/`로 수정 확인

### Step 8: 최종 테스트 및 검증
**Validation**:
- [ ] `uv run pytest backend/tests/` 통과 (100+ tests)
- [ ] `uv run ruff check .` 통과
- [ ] `uv run mypy backend/` 통과
- [ ] `docker-compose -f docker-compose.prod.yml up -d` 정상 실행
- [ ] Health checks: `curl http://localhost/health`, `curl http://localhost/api/topics`
- [ ] Refine Admin 접속: `http://localhost/admin/`

## Steps

### [ ] Step 1: Celery 작업을 FastAPI 서비스로 이동
- [ ] `api/services/ingestion.py` 생성 (PDF/Markdown/FAQ 파싱 로직)
- [ ] `api/routers/contexts.py` 업데이트 (Celery → ingestion service)
- [ ] `api/routers/admin/bulk_operations.py` 업데이트 (Celery 제거)
- [ ] 테스트: `api/tests/test_ingestion_service.py` (new)
- [ ] 검증: `uv run pytest api/tests/test_contexts.py api/tests/test_ingestion_service.py`

### [ ] Step 2: Django 코드 제거
- [ ] `core/`, `rag/`, `manage.py`, `templates/` 삭제
- [ ] `pyproject.toml` Django 의존성 제거
- [ ] `uv lock` 실행
- [ ] 검증: `uv run python -c "import django"` → ImportError

### [ ] Step 3: 폴더 구조 재구성
- [ ] `git mv api backend`
- [ ] `git mv admin-frontend frontend`
- [ ] Import 경로 업데이트 (api → backend)
- [ ] `alembic/env.py` 업데이트
- [ ] 검증: `uv run python -c "from backend.main import app"`, `cd frontend && npm run build`

### [ ] Step 4: Docker 구성 업데이트
- [ ] `docker-compose.prod.yml` 서비스 정리 (Django 제거)
- [ ] `Dockerfile.backend`, `Dockerfile.frontend` 생성
- [ ] Build context 업데이트
- [ ] 검증: `docker-compose -f docker-compose.prod.yml build`

### [ ] Step 5: Nginx 설정 업데이트
- [ ] `nginx/nginx.conf` Django admin 프록시 제거
- [ ] 검증: `curl http://localhost/api/topics`, `curl http://localhost/admin/`

### [ ] Step 6: 비즈니스 로직 테스트 이동
- [ ] `rag/tests/` → `backend/tests/` (ingestion, retrieval, golden dataset)
- [ ] Django TestCase → pytest
- [ ] 검증: `uv run pytest backend/tests/`

### [ ] Step 7: 문서 업데이트
- [ ] README.md 폴더 구조 업데이트
- [ ] DEPLOYMENT.md Django 제거 반영
- [ ] ARCHITECTURE.md 전환 완료 기록
- [ ] 검증: `grep -r "api/" docs/` → `backend/`

### [ ] Step 8: 최종 테스트 및 검증
- [ ] pytest 통과
- [ ] ruff, mypy 통과
- [ ] Docker Compose 프로덕션 빌드
- [ ] Health checks
- [ ] Refine Admin 접속

## Test/Validation Cases

### 기능 테스트
1. **FastAPI 엔드포인트**: GET/POST /api/topics, /api/contexts, /api/rag/ask
2. **Refine Admin**: Login, Topic/Context CRUD, Bulk operations
3. **Ingestion**: PDF/Markdown/FAQ 파싱 → 청킹 → 임베딩
4. **RAG**: 질문 → 검색 → 답변 생성
5. **Auth**: JWT 로그인, 권한 검증

### 통합 테스트
1. **Docker Compose**: 모든 서비스 정상 실행 (postgres, redis, qdrant, fastapi, frontend, nginx)
2. **Health Checks**: `/health`, `/api/topics`
3. **Nginx Proxy**: `/api/` → fastapi, `/admin/` → frontend

### 성능 테스트
1. **Golden Dataset**: 24 test cases (RAG 품질)
2. **Performance Benchmark**: 응답 시간, 메모리 사용량

## Rollback

### Step 1-2 실패 시
- `git checkout HEAD -- rag/tasks.py api/routers/contexts.py`
- Django 코드 복원 (git history)

### Step 3-4 실패 시
- `git mv backend api && git mv frontend admin-frontend`
- `docker-compose.prod.yml` 복원

### Step 5-8 실패 시
- 커밋별 롤백 (`git revert <commit>`)

## Review Hotspots

### Celery → FastAPI 서비스 이동 (Step 1)
- **Risk**: 비동기 작업 로직 누락
- **Review**: `rag/tasks.py` 5개 shared_task 모두 이동 확인
  - `process_document`
  - `ingest_pdf_document`
  - `ingest_markdown_document`
  - `ingest_faq_document`
  - `regenerate_embeddings`

### Import 경로 변경 (Step 3)
- **Risk**: 누락된 import로 런타임 에러
- **Review**: `grep -r "from api\." backend/` → 모두 `from backend.`로 변경 확인

### Docker 빌드 (Step 4)
- **Risk**: 빌드 컨텍스트 경로 오류
- **Review**: `docker-compose -f docker-compose.prod.yml build` 성공 확인

### 테스트 이동 (Step 6)
- **Risk**: Django 테스트 → pytest 전환 시 테스트 누락
- **Review**: Django 테스트 카운트 vs FastAPI 테스트 카운트 비교

## Status
- [x] Step 1: Celery → FastAPI 서비스 (api/services/ingestion.py 생성, 6/6 테스트 통과)
- [x] Step 2: Django 코드 제거 (core/, rag/, manage.py, templates/ 삭제, 20개 패키지 제거)
- [x] Step 3: 폴더 구조 재구성 (api → backend, admin-frontend → frontend)
- [ ] Step 4: Docker 구성 업데이트
- [ ] Step 5: Nginx 설정 업데이트
- [ ] Step 6: 비즈니스 로직 테스트 이동
- [ ] Step 7: 문서 업데이트
- [ ] Step 8: 최종 테스트 및 검증
