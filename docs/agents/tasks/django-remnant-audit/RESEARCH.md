# Research: Django Remnant Audit

## Goal
- Identify any remaining Django-specific code, dependencies, or configuration after migration to FastAPI.

## Scope
- Source tree (Python, frontend, scripts) for Django references.
- Environment variables, configuration files, and docs.
- Tooling (tests, scripts, Docker, CI).

## Related Files/Flows
- backend configuration, env examples, docker compose files.
- Tests invoking Django manage commands.
- Deployment/docs referencing Django services.

## Hypotheses
- Django references may persist in environment variable names or docs.
- Some scripts/tests might still call `python manage.py` or Django settings modules.
- Docker configs could retain Django services or ports.

## Evidence
- [Resolved] `backend/retrieval/` modules (`rag.py`, `embeddings.py`, `cache.py`, `monitoring.py`, `qdrant.py`) imported `django.conf.settings`/`django.core.cache`; now rely on `backend.config.Settings`, SQLAlchemy sessions, and Redis/in-memory caches.
- [Resolved] `backend/services/rag_service.py` comments referenced Django; service now fully decoupled and references SQLAlchemy-backed lookups.
- [Resolved] `backend/config.py` attempted to derive DB config from Django settings; removed fallback and defined explicit FastAPI settings fields.
- [Resolved] Dev tooling previously retained Django defaults (`Dockerfile.dev`, `docker-compose.dev.yml`, `scripts/docker/dev-entrypoint.sh` using `manage.py runserver`); now delegate to uvicorn/Async FastAPI workflows only.
- [Resolved] Deployment script `scripts/deploy.sh` used Django management commands; rewritten to run Alembic migrations and manage FastAPI services.
- Alembic environment still excludes `django_migrations` table for legacy schema compatibility (follow-up decision needed on table retirement).
- [Resolved] Environment samples `.env.example` and `.env.prod.example` referenced Django engines/email backends; updated to FastAPI terminology and defaults.
- [Resolved] Core documentation (`docs/ADMIN_GUIDE.md`, `docs/PRODUCTION_DOCKER.md`, `docs/CONTRIBUTING.md`, etc.) refreshed to describe FastAPI + Refine flows; legacy references archived or annotated.
- Backend test suite retains skips referencing Django-era fixtures; need Postgres-backed strategy to replace them.
- [Resolved] `docker-compose.dev.yml` no longer runs dual-stack Django/FastAPI; now only boots the FastAPI backend container with reload.

## Assumptions / Open Questions
- Need clarity on whether legacy Django DB tables (e.g., `django_migrations`) remain intentionally for historical data.
- Determine if any deployment workflows still rely on Django for auth management before removing scripts.
- Confirm target caching backend for RAG service (Redis vs. legacy Django cache).

## Sub-agent Findings
- _N/A_

## Risks
- False positives if Django keyword used in historical notes only.

## Next
- Inventory codebase for `django` mentions and collect evidence.
