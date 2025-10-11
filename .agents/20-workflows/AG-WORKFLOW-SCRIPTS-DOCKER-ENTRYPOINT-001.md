---
id: AG-WORKFLOW-SCRIPTS-DOCKER-ENTRYPOINT-001
version: 1.0.0
scope: folder:scripts/docker
status: active
supersedes: []
depends: [AG-WORKFLOW-SCRIPTS-USAGE-001]
last-updated: 2025-10-11
owner: platform-team
---
# Docker Entrypoint Script Flow

## Intent
- Keep the backend container bootstrap deterministic across macOS and Linux Docker Desktop environments.
- Provide a resilient developer experience even when the shared `uv` environment becomes invalid.

## Execution Notes
- Script path: `scripts/docker/dev-entrypoint.sh`.
- Rebuilds the `/opt/uv` (or `$UV_PROJECT_ENVIRONMENT`) environment via `uv sync --dev` if Python executables are missing.
- Default command: `uv run uvicorn main:app --reload --host 0.0.0.0 --port 8001`.
- Forwards any additional arguments to support ad-hoc container commands.

## Constraints
- Stick to POSIX shell syntax; exit immediately on failures.
- Respect volume mounts so repeated container restarts remain idempotent.
