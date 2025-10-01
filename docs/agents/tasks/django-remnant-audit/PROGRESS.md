# Progress: Django Remnant Audit

## Summary
- Removed Django dependencies from runtime code, tooling, and documentation; guard tests now pass.

## Goal & Approach
- Use ripgrep sweeps and targeted refactors to ensure no active Django code paths remain in the FastAPI stack.

## Completed Steps
- Ran repo-wide search for "django" references and catalogued affected modules/config/docs.
- Bucketed findings into runtime-critical code, tooling/environment, and documentation follow-ups.
- Added failing pytest guard for Django imports, then refactored backend modules until it passed.
- Updated backend retrieval layer to rely on SQLAlchemy + Redis/Redis-backed caches instead of Django settings/cache.
- Replaced Django-centric tooling (Dockerfile.dev, docker-compose.dev.yml, deploy/test scripts, .env templates) with FastAPI-native equivalents.
- Refreshed key documentation (`ADMIN_GUIDE.md`, `ENVIRONMENT.md`, `PRODUCTION_DOCKER.md`, `docs/agents/AGENTS.md`, `backend/README.md`, contributing guides).

## Current Failures
- Full `uv run pytest` currently fails because SQLite fixtures do not create legacy `auth_user`/context tables; requires Postgres-backed setup or fixture updates.

## Decision Log
- Django ORM/cache references in backend services were removed in favor of SQLAlchemy sessions + in-memory/Redis caching.
- Documentation now references FastAPI workflows; legacy Django guides archived within historical ADR notes only.

## Next Step
- Step 6: align test harness with FastAPI-only stack (bootstrap Postgres test container or adjust fixtures to seed required tables) to restore green suite.
