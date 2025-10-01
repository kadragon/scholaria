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

## Next Step
Step 5: Nginx 설정 업데이트
