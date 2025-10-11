---
id: AG-WORKFLOW-SCRIPTS-USAGE-001
version: 1.0.0
scope: folder:scripts
status: active
supersedes: []
depends: [AG-POLICY-SCRIPTS-QUALITY-001]
last-updated: 2025-10-11
owner: platform-team
---
# Script Usage Patterns

## `scripts/test_docker_integration.sh`
- Prefers `docker compose`; auto-falls back to `docker-compose`.
- Waits for postgres, redis, and qdrant health before running migrations.
- Executes `uv run alembic upgrade head` followed by `uv run pytest tests/test_rag_endpoint.py tests/test_rag_streaming.py -v --tb=short` (command run from the `backend/` directory).
- Leaves containers running; remind callers to invoke `${COMPOSE_CMD[*]} down` during teardown.

## `scripts/docker/dev-entrypoint.sh`
- Rebuilds the `/opt/uv` environment with `uv sync --dev` if missing.
- Launches `uv run uvicorn main:app --reload --host 0.0.0.0 --port 8001`.
