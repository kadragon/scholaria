---
id: AG-POLICY-DEV-GUARDRAILS-001
version: 1.0.0
scope: global
status: active
supersedes: []
depends: [AG-FOUND-INTENT-001]
last-updated: 2025-10-11
owner: team-admin
---
# Development Guardrails

## Core Practices
- Apply strict TDD: move through Red → Green → Refactor without skipping stages.
- Keep the codebase linted and typed: `(cd backend && uv run ruff check .)`, `(cd backend && uv run ruff format --check .)`, and `(cd backend && uv run mypy .)` must pass before any commit.
- Anchor all backend tests under `backend/tests/`; ensure suites remain race-free under parallel execution.

## Runtime Environments
- Standardize on Python 3.13+ with the `uv` package manager.
- Operate development and production environments through `docker compose` (`docker-compose.yml` for dev, `docker-compose.prod.yml` for prod).
- Keep Alembic migrations at head; update `backend/tests/test_alembic_migrations.py` with new revisions and adopt sequential numeric prefixes where feasible while tolerating legacy hashed IDs.

## Resilience Expectations
- Redis failures must degrade gracefully by disabling caches without breaking RAG flows.
- Ensure Docling remains the sole document parsing dependency; no fallback to external Unstructured APIs.
- Enforce health checks for backend, PostgreSQL, Redis, and Qdrant during integration tests.
