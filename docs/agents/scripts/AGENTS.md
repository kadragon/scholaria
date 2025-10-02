# Scripts Folder - Agent Knowledge Base

## Intent

Automation helpers (shell scripts, tooling wrappers) supporting Scholaria workflows.

## Constraints

- Keep scripts POSIX-compatible; avoid Bash 5+ only features when possible.
- Surface clear logging with emoji-friendly prefixes used across existing scripts.
- Guard against missing dependencies (Docker, uv) and fail fast with actionable errors.
- Reflect current service topology (Docling runs in-process; no Unstructured API container).

## Context

- `test_docker_integration.sh` orchestrates Docker Compose bring-up and runs integration tests with `DOCKER_INTEGRATION_TESTS=true`.
- `scripts/docker/dev-entrypoint.sh` guarantees uv dependencies exist before launching the FastAPI backend server inside Docker.
- Required services: PostgreSQL, Redis, Qdrant; optional: MinIO. Docling does not require a separate health check.
- Update helper arrays and health-check logic whenever `docker-compose.yml` services change.

## Changelog

- 2025-09-22: MVP completion - all automation scripts validated for production deployment
- 2025-09-20: Removed Unstructured API health checks; script now assumes Docling dependency is installed via Python packages.
