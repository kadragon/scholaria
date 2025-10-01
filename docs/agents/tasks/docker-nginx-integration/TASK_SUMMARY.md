# Task Summary: Docker & Nginx Integration

## Goal
FastAPI + Refine Admin Panel을 Nginx를 통해 프로덕션 Docker 환경에 통합

## Key Changes

### Docker Configuration
- `docker-compose.prod.yml`: FastAPI (8001) + admin-frontend (80) 서비스 추가
- `Dockerfile.admin`: Multi-stage build (Node builder → Nginx runtime)
- Build args: `VITE_API_URL=/api`, `VITE_BASE_PATH=/admin/`

### Nginx Configuration
- `nginx/nginx.conf`:
  - `/api/` → fastapi:8001
  - `/admin/` → admin-frontend:80 (SPA fallback)
  - `/docs/` → fastapi:8001
- `nginx/admin-frontend.conf`: SPA static serving with `try_files` fallback

### FastAPI CORS
- `api/config.py`: `FASTAPI_ALLOWED_ORIGINS` 환경 변수 + `cors_origins` 프로퍼티
- `api/main.py`: 하드코딩된 origins → `settings.cors_origins` 사용

### Frontend Configuration
- `admin-frontend/vite.config.ts`: `base: VITE_BASE_PATH || "/admin/"`
- `admin-frontend/src/App.tsx`: `BrowserRouter basename` 추가
- `admin-frontend/.env.example`: `VITE_BASE_PATH=/admin/` 추가

### Environment Documentation
- `.env.example`: `FASTAPI_ALLOWED_ORIGINS` 개발 기본값
- `.env.prod.example`: `FASTAPI_ALLOWED_ORIGINS`, `VITE_API_URL`, `VITE_BASE_PATH` 프로덕션 예시

## Tests
- `api/tests/test_app_cors.py`: 4개 CORS 테스트 (preflight, actual request, credentials, env integration)
- `rag/tests/test_docker_prod_configuration.py`: 3개 Docker compose 회귀 테스트
- 40/40 테스트 통과

## Commit SHAs
(To be added after commit)

## Impact
- 프로덕션 배포 준비 완료
- 개발/프로덕션 환경 분리 (CORS origins, API URL, base path)
- Nginx를 통한 단일 엔트리포인트 (80/443)
