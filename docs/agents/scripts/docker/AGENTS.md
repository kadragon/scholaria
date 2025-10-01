# Scripts/Docker - Agent Knowledge Base

## Intent

Document container entrypoints that prepare local development environments.

## Constraints

- POSIX shell only; support macOS + Linux Docker Desktop.
- Must run safely when volumes override image state (idempotent bootstrapping).
- Keep uv commands non-interactive and fail fast on dependency resolution errors.

## Context

- `dev-entrypoint.sh` rehydrates the uv environment at `/opt/uv` if bind mounts replaced it.
- Delegates to `uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001` unless overridden by extra arguments.

## Changelog

- Added uv bootstrap guard to prevent missing virtualenv when the host project folder is mounted.
