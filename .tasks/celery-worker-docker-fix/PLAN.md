# Plan: Celery Worker Docker Fix

## Implementation Steps
1. Create `scripts/docker/celery-entrypoint.sh` to bootstrap an isolated uv environment (default `/opt/uv/backend-worker`) and launch `uv run celery -A celery_app worker`.
2. Update `docker-compose.yml` to invoke the new entrypoint for the `celery-worker` service and expose the `UV_PROJECT_ENVIRONMENT` path outside the bind mount.
3. Verify the worker starts cleanly:
   - `docker compose build celery-worker`
   - `docker compose up celery-worker`
   - `docker compose run --rm celery-worker sh -c "cd backend && uv run celery -A celery_app inspect ping"`
4. Remove any temporary containers and document the outcome in `.tasks/celery-worker-docker-fix/PROGRESS.md`.

## Rollback Strategy
- Revert the new entrypoint script and restore the original `docker-compose.yml` command stanza.
- Run `docker compose up celery-worker` to confirm the service still fails fast (baseline), then revisit alternative options (dedicated image).
