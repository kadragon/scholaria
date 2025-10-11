# Research: Celery Worker Docker Container Fails to Start

## Summary
- **Symptom**: `docker compose up celery-worker` exits immediately with `sh: 1: /app/.venv/bin/python3: not found`.
- **Impact**: Five Playwright tests that rely on RAG responses remain skipped because Celery never processes background jobs.

## Evidence Collected
- `docker-compose.yml` currently runs the worker via `sh -c "cd backend && /app/.venv/bin/python3 -m celery -A celery_app worker --loglevel=info"`, assuming a venv at `/app/.venv`.
- `docker compose logs celery-worker --tail=40` on 2025-10-11 reproduced the failure: `sh: 1: /app/.venv/bin/python3: not found`.
- The bind mount `.:/app` introduces host-side virtual environments:
  - `/app/backend/.venv/bin/celery` exists but its shebang points to the host path `#!/Users/kadragon/Dev/scholaria/.venv/bin/python3`.
  - `/app/.venv/bin/celery` may also appear, creating ambiguity around which interpreter is invoked.
- `Dockerfile.backend` (development stage) already installs `uv` at `/bin/uv` and syncs dependencies into `/app/backend/.venv` during the image build.

## Root Cause
1. When the repo is bind-mounted into the container, any host-managed `.venv` folders shadow the image's baked virtual environment.
2. Executable scripts inside those host venvs hard-code the host interpreter path in their shebangs, which does not exist inside the container.
3. The compose command explicitly invokes `/app/.venv/bin/python3`, further coupling the container to the host venv layout.

## Constraints & Considerations
- Retain live-code reload during development (bind mount cannot be removed entirely).
- Avoid reinstalling Celery on every container start (startup time).
- Reuse the existing `uv` workflow for dependency management to stay aligned with backend service conventions.
- Production `docker-compose.prod.yml` already works (no bind mounts), so all changes must remain scoped to the dev stack.

## Candidate Approaches
1. **Dedicated Celery image without bind mounts** — reliable but sacrifices hot reload for the worker.
2. **Entrypoint script that rebuilds Celery inside the mounted tree** — fixes shebangs but incurs ~5s reinstall penalty on every restart.
3. **Isolate the worker venv outside the bind mount and launch via `uv run`** — keeps hot reload while preventing host venv contamination.

## Decision
- Proceed with **Option 3**: add a Docker entrypoint script that bootstraps a container-local uv environment (e.g., `/opt/uv/backend-worker`) and runs `uv run celery -A celery_app worker --loglevel=info`. This avoids host path leakage and keeps startup lightweight after the initial sync.
