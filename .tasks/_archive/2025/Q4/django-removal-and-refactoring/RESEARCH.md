# Research: Django 제거 및 프로젝트 구조 리팩토링

## Goal
Django 레거시 제거 및 프로젝트 구조를 FastAPI 중심으로 정리

## Scope
- Django 코드 제거 (`core/`, `rag/`, `manage.py`, templates/, Django settings)
- 폴더 구조 재구성 (Option B → 모노레포)
- Docker Compose 빌드 컨텍스트 정리
- 문서 업데이트
- 최종 테스트 (모든 테스트 FastAPI 환경에서 재실행)

## Related Files/Flows

### Django 레거시 (제거 대상)
- **Django core**: `core/` (settings, urls, wsgi, celery, health checks)
- **Django app**: `rag/` (admin, models, views, urls, tasks, templates)
- **Django management**: `manage.py`
- **Templates**: `templates/` (admin, rag, base.html)
- **Static files**: `static/`, `staticfiles/`
- **Dockerfile**: `Dockerfile.prod` (Django-specific build)

### FastAPI 현재 구조 (유지)
- **API**: `api/` (routers, models, schemas, services, dependencies, tests)
- **Admin Frontend**: `admin-frontend/` (Refine + React + shadcn/ui)
- **Alembic**: `alembic/` (migrations)
- **Nginx**: `nginx/` (reverse proxy config)

### Docker 구조 (재구성 필요)
- `docker-compose.prod.yml`: Django (`web`, `celery-worker`, `celery-beat`) 제거
- `Dockerfile.prod`: Django 의존성 제거, FastAPI 전용으로 변경
- `Dockerfile.admin`: 유지 (admin-frontend 빌드)

### 테스트 (재실행 필요)
- **Django 테스트** (제거):
  - `rag/tests/test_admin.py` (Django admin)
  - `rag/tests/test_ui_enhancements.py` (Django templates)
  - `rag/tests/test_dynamic_form_javascript.py` (Django forms)
  - `core/tests/` (Django health checks, logging)
- **FastAPI 테스트** (유지 & 확장):
  - `api/tests/` (40개 테스트)
  - 추가 필요: 기존 Django 비즈니스 로직 테스트 (ingestion, retrieval)

## Hypotheses

### H1: Django 제거 후에도 FastAPI는 모든 기능을 제공할 수 있다
**Evidence**:
- ✅ Phase 6 완료: Refine Admin Panel이 Django admin 대체
- ✅ Phase 3-5 완료: RAG, Write API, Auth 모두 FastAPI로 포팅
- ✅ Celery는 FastAPI에서 필요 없음 (FastAPI Write API는 동기 처리, Celery signal 미작동)

**Risk**: Celery 비동기 작업 (임베딩 생성, PDF 파싱)이 FastAPI로 전환되지 않음
- **Mitigation**: `rag/tasks.py` 로직을 FastAPI 서비스 레이어로 이동 (`api/services/ingestion.py`)

### H2: 폴더 구조 재구성은 Docker 빌드를 깨뜨리지 않는다
**Evidence**:
- 현재 `docker-compose.prod.yml`의 build context는 `.` (루트)
- `api/`, `admin-frontend/` 폴더 이동 시 Dockerfile 경로 조정 필요

**Plan**:
```
scholaria/
├── backend/          (← api/)
│   ├── routers/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── dependencies/
│   ├── tests/
│   └── main.py
├── frontend/         (← admin-frontend/)
│   ├── src/
│   ├── public/
│   └── package.json
├── alembic/
├── nginx/
├── scripts/
├── docs/
├── docker-compose.prod.yml
└── pyproject.toml
```

**Docker 변경**:
- `Dockerfile.backend`: `COPY backend/ /app/backend/`
- `Dockerfile.frontend`: `COPY frontend/ /app/frontend/`
- `docker-compose.prod.yml`: `build.context: ./backend`, `build.context: ./frontend`

### H3: 테스트는 모두 FastAPI 환경에서 재실행 가능하다
**Current State**:
- Django 테스트: 381개 중 ~50개는 Django admin/template 테스트
- FastAPI 테스트: 40개 (topics, contexts, history, rag, auth, admin)
- 비즈니스 로직 테스트: ingestion (chunkers, parsers), retrieval (qdrant, embeddings, reranking), golden dataset

**Action**:
1. Django admin/template 테스트 제거 (불필요)
2. 비즈니스 로직 테스트를 FastAPI 환경에서 재실행 (`api/tests/`)
3. 통합 테스트 (Docker) 업데이트

## Assumptions/Open Qs

### Assumptions
1. Celery 제거 가능 (FastAPI Write API는 동기 처리, 비동기 워크플로우 불필요)
2. Django ORM → SQLAlchemy 전환 완료 (Phase 1-6)
3. Django admin → Refine Admin 전환 완료 (Phase 6.2)
4. 기존 데이터베이스 스키마 유지 (Alembic 마이그레이션)

### Open Qs
1. **Q: Celery 작업을 FastAPI로 어떻게 이동?**
   - A: `rag/tasks.py` 로직을 `api/services/ingestion.py`로 이동 (sync/async 함수)
   - Context 생성 시 임베딩 생성은 동기 처리 (현재도 FastAPI Write API에서 처리)

2. **Q: 폴더 구조 변경 시 기존 개발자 경험 유지?**
   - A: `scripts/` 폴더에 alias 추가 (`cd backend`, `cd frontend`)
   - README 업데이트 (새 폴더 구조 설명)

3. **Q: Django 제거 후 최종 테스트 범위?**
   - A: FastAPI 테스트 (40개) + 비즈니스 로직 테스트 (ingestion, retrieval, golden dataset)
   - 목표: 최소 100개 테스트 통과

4. **Q: 프로덕션 배포 시 Django 제거 영향?**
   - A: `docker-compose.prod.yml`에서 `web`, `celery-worker`, `celery-beat` 제거
   - Nginx 설정 업데이트 (`/admin/` → Django admin 제거)

## Sub-agent Findings
N/A (단순 리팩토링 작업, sub-agent 불필요)

## Risks

### High Risk
1. **Celery 작업 누락**: `rag/tasks.py`의 비동기 작업을 FastAPI로 이동하지 않으면 임베딩 생성 실패
   - Mitigation: Step-by-step 이동, 각 작업별 테스트
2. **Docker 빌드 실패**: 폴더 구조 변경 시 Dockerfile 경로 오류
   - Mitigation: 로컬 Docker 빌드 테스트 후 커밋

### Medium Risk
1. **테스트 누락**: Django 테스트 제거 시 비즈니스 로직 테스트 누락
   - Mitigation: Django 테스트 → FastAPI 테스트 매핑 테이블 작성
2. **문서 동기화**: README, DEPLOYMENT, ARCHITECTURE 업데이트 누락
   - Mitigation: 문서 업데이트를 별도 Step으로 분리

### Low Risk
1. **개발 경험 저하**: 폴더 구조 변경 시 기존 경로 찾기 어려움
   - Mitigation: README에 폴더 구조 설명 추가

## Next
PLAN.md 작성 (8단계 상세 계획)
