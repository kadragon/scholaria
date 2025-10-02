# Research: Docker & Nginx Integration

## Goal
- Deliver Phase 6.3 by wiring the FastAPI backend and Refine admin frontend into the production-ready Docker + Nginx stack so that `/api` traffic hits FastAPI (port 8001) and `/admin` serves the SPA bundle.

## Scope
- Container orchestration: `docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.prod.yml`.
- Build artifacts: new admin frontend image (multi-stage Node→Nginx) and FastAPI runtime image if required.
- Web tier configuration: reverse proxy rules under `nginx/nginx.conf` (and any split files, e.g. `nginx/admin.conf`).
- API app settings impacting CORS (`api/main.py`, `.env.*`).
- Admin frontend environment config (`admin-frontend/src/providers/*`, Vite build expectations).

## Related Files/Flows
- `docker-compose.dev.yml`: currently runs Django `web` and FastAPI `fastapi` containers from `Dockerfile.dev` on ports 8000/8001.
- `docker-compose.prod.yml`: production stack with Django web/celery, but no FastAPI or admin-frontend service yet; optional `nginx` service proxies only to Django (`nginx/nginx.conf`).
- `Dockerfile.prod`: builds Django/Celery image `web`/`celery-*` use today.
- `admin-frontend/package.json`, `vite.config.ts`, `src/providers/{dataProvider,authProvider}.ts`: admin SPA expects `VITE_API_URL` pointing at FastAPI REST endpoints.
- `api/main.py`: FastAPI entrypoint with CORS whitelist for local hosts only.
- `scripts/docker/dev-entrypoint.sh`, `fastapi-dev-entrypoint.sh`: existing dev runtime helpers.

## Hypotheses
1. Production compose needs a dedicated FastAPI image (either reuse Django build or introduce new Dockerfile) to serve `/api` endpoints decoupled from Django during migration.
2. Admin SPA should be built once and served as static assets by the Nginx container; development compose can mount the local build for rapid iteration.
3. Nginx must expose separate upstreams for Django (legacy) and FastAPI (port 8001) and map `/admin` + SPA routes accordingly while keeping `/` default to Django until Phase 7/8.
4. FastAPI requires updated CORS origins to include production domain(s) and admin SPA base URL.

## Evidence
- `docker-compose.prod.yml` defines services for Django web, celery worker/beat, postgres, redis, qdrant, nginx but lacks any FastAPI or admin frontend containers; `nginx` upstream currently targets only `web:8000`.
- `nginx/nginx.conf` routes `/api` to the `django` upstream and serves `/admin` via Django; no SPA-specific `try_files` handling.
- `admin-frontend` bundle references `import.meta.env.VITE_API_URL` defaulting to `http://localhost:8001/api`, meaning production must supply a proper environment value at build time.
- `api/main.py` CORS whitelist is hard-coded to localhost origins, so browser calls from a production domain would be blocked.

## Assumptions / Open Questions
- Will Phase 6.3 run Django + FastAPI side by side in production (likely yes until Phase 8 removes Django)? Need confirmation on whether `/` should still proxy to Django.
- Decide whether to create a dedicated `Dockerfile.fastapi` or reuse `Dockerfile.prod` with different command (Gunicorn vs Uvicorn). Current instructions favor a new build context to keep responsibilities separate.
- Determine location for admin SPA Nginx config snippet: reuse `nginx/nginx.conf` or create `nginx/admin.conf` included by main file.

## Sub-agent Findings
- None (single-agent research pass).

## Risks
- Misconfigured proxy routes could break existing Django admin/web endpoints during migration.
- Serving SPA without proper cache headers or `try_files` fallback may break client-side routing.
- Incomplete CORS setup would block JWT-authenticated admin requests.
- Docker image build cache may grow; multi-stage builds must prune dev dependencies.

## Next
- Draft implementation plan covering tests (compose + nginx config assertions), container definitions, CORS updates, and environment variable plumbing.
