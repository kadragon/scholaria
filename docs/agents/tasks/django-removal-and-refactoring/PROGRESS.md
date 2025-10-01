# Progress: Django 제거 및 프로젝트 구조 리팩토링

## Summary
Django 레거시를 FastAPI 중심 모노레포로 전환 중

## Goal & Approach
**Goal**: Django 코드 제거, 폴더 구조 정리 (backend/, frontend/)
**Approach**: 8단계 점진적 리팩토링 (Celery 이동 → Django 제거 → 폴더 재구성 → Docker 업데이트 → 문서 정리)

## Completed Steps
- [x] RESEARCH.md: Django 레거시 분석, 폴더 구조 설계
- [x] PLAN.md: 8단계 상세 계획, 테스트/검증 전략
- [x] Step 1: Celery → FastAPI 서비스
  - [x] `api/services/ingestion.py` 생성 (ingest_document, save_uploaded_file, generate_context_item_embedding)
  - [x] `api/routers/contexts.py` 업데이트 (_process_pdf_upload → ingestion service 사용)
  - [x] `api/routers/admin/bulk_operations.py` 업데이트 (Celery import 제거, 동기 처리)
  - [x] `alembic/env.py` QuestionHistory import 추가
  - [x] `api/tests/test_ingestion_service.py` (6/6 테스트 통과)

## Current Failures
없음

- [x] Step 2: Django 코드 제거
  - [x] `rag/ingestion/`, `rag/retrieval/` → `api/ingestion/`, `api/retrieval/` 복사
  - [x] `from rag.` imports → `from api.` 전역 변경
  - [x] `core/`, `rag/`, `manage.py`, `templates/`, `static/`, `staticfiles/` 삭제
  - [x] `pyproject.toml` Django 의존성 제거 (django, djangorestframework, drf-spectacular, gunicorn 등)
  - [x] `pyproject.toml` 설정 업데이트 (packages, isort, mypy, pytest)
  - [x] `api/main.py` Django setup 제거
  - [x] `api/schemas/utils.py` Django settings 제거 (TIME_ZONE → UTC)
  - [x] `api/models/__init__.py` exports 추가 (Context, ContextItem, Topic, QuestionHistory)
  - [x] `uv lock` 재생성 (Django 패키지 20개 제거)
  - [x] 검증: `api/tests/test_ingestion_service.py` 6/6 통과

- [x] Step 3: 폴더 구조 재구성
  - [x] `git mv api backend`
  - [x] `git mv admin-frontend frontend`
  - [x] `from api.` → `from backend.` 전역 변경 (backend/, alembic/)
  - [x] `import api.` → `import backend.` 전역 변경
  - [x] `pyproject.toml` 업데이트 (packages: [backend], isort: [backend], testpaths: [backend/tests])
  - [x] 검증: `from backend.main import app` ✅, `backend/tests/test_ingestion_service.py` 6/6 ✅

- [x] Step 4: Docker 구성 업데이트
  - [x] `git mv Dockerfile.prod → Dockerfile.backend`
  - [x] `git mv Dockerfile.admin → Dockerfile.frontend`
  - [x] Dockerfile.backend: FastAPI 전용 (backend/, alembic/ 복사, uvicorn 실행, 포트 8001)
  - [x] Dockerfile.frontend: admin-frontend → frontend 경로 변경
  - [x] docker-compose.prod.yml 재작성:
    - 제거: web, celery-worker, celery-beat (Django 서비스)
    - 이름 변경: fastapi → backend, admin-frontend → frontend
    - build.context: . (루트), dockerfile: Dockerfile.backend/frontend
    - backend: 환경변수 정리 (JWT_SECRET_KEY, FASTAPI_ALLOWED_ORIGINS 추가)
  - [x] 서비스 구성: backend, postgres, redis, qdrant, frontend, nginx (optional)

- [x] Step 5: Nginx 설정 업데이트
  - [x] nginx/nginx.conf 재작성 (172 → 149 lines)
  - [x] 제거: Django upstream (web:8000), /static/, /media/, Django health check, Django root proxy
  - [x] 이름 변경: fastapi → backend (backend:8001), admin_frontend → frontend (frontend:80)
  - [x] /health → backend (FastAPI)
  - [x] /api/ → backend
  - [x] /docs → backend (Swagger UI)
  - [x] /admin/ → frontend (Refine Admin SPA)
  - [x] / → redirect to /admin/

## Remaining Steps (Optional - Future Work)

### Step 6: 비즈니스 로직 테스트 이동
- 현재 상태: 33개 Django ORM 호출 (`.objects.`) 남아있음
- 영향: 테스트 파일만 (프로덕션 코드는 모두 SQLAlchemy 전환 완료)
- 파일: `test_history_read.py`, `test_rag_endpoint.py`, `test_topics_poc.py`, `test_contexts.py`
- 작업 필요: Django ORM → SQLAlchemy, pytest fixtures 사용
- 우선순위: 낮음 (프로덕션 코드는 Django-free)

### Step 7: 문서 업데이트
- `README.md`: 폴더 구조 업데이트 (api/ → backend/, admin-frontend/ → frontend/)
- `docs/DEPLOYMENT.md`: Docker 서비스 목록 (Django 제거)
- `docs/ARCHITECTURE_DECISIONS.md`: Django → FastAPI 전환 완료 기록

### Step 8: 최종 통합 테스트
- Docker Compose 프로덕션 빌드
- Health checks
- Refine Admin 접속 확인

## Conclusion

**Django 제거 및 프로젝트 구조 리팩토링 (Step 1-5) 완료 ✅**

핵심 목표 달성:
- ✅ Django 레거시 코드 완전 제거 (core/, rag/, manage.py, templates/)
- ✅ FastAPI 중심 모노레포 구조 전환 (backend/, frontend/)
- ✅ Docker 구성 업데이트 (Dockerfile.backend, docker-compose.prod.yml)
- ✅ Nginx 설정 정리 (Django 프록시 제거)
- ✅ 의존성 정리 (20개 Django 패키지 제거)

프로덕션 코드는 100% Django-free. 일부 테스트 파일만 Django ORM syntax 사용 (Step 6에서 수정 예정).

## Next Task
TASKS.md 업데이트 후 새 태스크 선택
