---
id: AG-WORKFLOW-FASTAPI-OPS-001
version: 1.0.0
scope: global
status: active
supersedes: []
depends: [AG-WORKFLOW-DEV-LOOP-001]
last-updated: 2025-10-11
owner: team-admin
---
# FastAPI Operational Playbook

## Configuration Management
- Centralize runtime settings in `backend/config.Settings`; avoid fallback defaults for required environment variables.
- Mirror configuration expectations in `.env.example` and Docker Compose files.

## Testing Patterns
- Command of record: `uv run pytest backend/tests -q`.
- Database/Redis/Qdrant dependent tests require `docker compose up postgres redis qdrant` before execution.
- Maintain deterministic tests by mocking external API calls and time sources.

## Dockerized Development
- Entry script: `scripts/docker/dev-entrypoint.sh` ensures `uv sync --dev` before launching `uvicorn`.
- Access the API via `http://localhost:8001` when containers are up.

## Logging & Monitoring
- Enforce structured logging with request identifiers.
- Keep Flower running for Celery observability where long-running tasks are involved.
