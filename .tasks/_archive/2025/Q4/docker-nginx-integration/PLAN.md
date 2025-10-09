# Plan: Docker & Nginx Integration

## Objective
- Ship Phase 6.3 by wiring FastAPI + Refine admin into the Docker/Nginx stack so `/api` hits FastAPI (8001) and `/admin` serves the SPA bundle, keeping Django web functional during migration.

## Constraints
- Strict TDD: each behaviour covered by failing test before implementation.
- No downtime for existing Django routes; compose defaults must remain backwards-compatible.
- Avoid breaking current dev workflow (docker-compose.dev.yml stays intact).

## Target Files & Changes
- `docker-compose.prod.yml`: add `fastapi` and `admin-frontend` services, update `nginx` routing/depends.
- `Dockerfile.admin` (new) + `nginx/admin-frontend.conf` for SPA image.
- `nginx/nginx.conf`: new upstream for FastAPI/admin frontend, route adjustments (`/api`, `/admin`, `/docs`).
- `api/main.py` (and possibly `api/config.py`): configurable CORS origins.
- `.env.example` / deployment docs for new variables (`FASTAPI_ALLOWED_ORIGINS`, `VITE_API_URL`, etc.).
- Tests under `rag/tests/` and `api/tests/` to guard compose/nginx/cors expectations.

## Test / Validation Cases
- `uv run pytest rag/tests/test_docker_fastapi_service.py` (regression) + new compose/nginx tests.
- `uv run pytest api/tests/test_app_cors.py` (new) to ensure env-driven origins.
- Targeted admin API smoke (`uv run pytest api/tests/admin/test_topics.py -q`) after changes to ensure no regressions.

## Steps
- [x] Step 1: Write failing tests covering production compose + nginx proxy expectations.
- [x] Step 2: Implement compose updates, new Dockerfile/admin config, and nginx changes to satisfy tests.
- [ ] Step 3: Add failing tests for configurable CORS origins.
- [ ] Step 4: Implement CORS/env plumbing and update docs/examples.
- [ ] Step 5: Run targeted test suite, update PLAN status & PROGRESS, and prepare final summary.

## Rollback Strategy
- Revert modifications to compose files, nginx configs, FastAPI CORS changes, and remove new Dockerfile if issues arise; ensure tests revert alongside config to previous passing state.

## Review Hotspots
- Ensure nginx syntax correctness (`docker run --rm nginx:alpine nginx -t` optional manual check).
- Compose indentation & YAML anchors; keep environment secrets externalized.
- Validate env var docs so deployers know to rebuild admin image when VITE variables change.

## Status
- [x] Step 1: tests added & failing.
- [x] Step 2: compose/nginx implementation complete.
- [x] Step 3: CORS tests added (4 tests in test_app_cors.py).
- [x] Step 4: CORS implementation + docs ready (config.py, main.py, .env files, vite config, Dockerfile).
- [x] Step 5: Tests green (40/40 passed) and docs updated.
