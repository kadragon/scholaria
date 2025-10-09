# Research: FastAPI Test Harness Alignment

## Goal
- Restore a green `uv run pytest` by migrating the test harness from Django-era SQLite fixtures to a FastAPI/PostgreSQL-compatible setup.

## Scope
- Backend pytest configuration, fixtures, and database bootstrap scripts.
- Docker/CI workflows that spin up databases for tests.
- Documentation referencing test commands or prerequisites.

## Related Files/Flows
- `backend/tests/conftest.py`, fixtures creating users/contexts.
- `backend/models/*`, Alembic migrations, `alembic/env.py`.
- `docker-compose.yml`, `docker-compose.dev.yml`, CI pipeline config (if present).
- `scripts/test_docker_integration.sh`, other scripts invoking tests.

## Hypotheses
- Tests currently assume legacy Django-managed SQLite in-memory DB with `auth_user` table.
- FastAPI fixtures need explicit Alembic migration runs or SQLAlchemy metadata creation before tests.
- Switching to Postgres test container (or file-based SQLite) will eliminate missing-table errors.

- `uv run pytest` fails: `sqlite3.OperationalError: no such table: auth_user` (FastAPI TestClient login step).
- Many admin/context tests rely on seeded data previously provided by Django fixtures.
- `backend/tests/conftest.py` may still import Django utilities or expect ORM-managed tables.
- Conftest currently spins up per-worker SQLite files (`test_api[_gwX].db`) via `Base.metadata.create_all`, but tables missing during async TestClient usage indicates schema bootstrap race and lack of Alembic coverage (e.g., auth_user).
- Alembic migrations target PostgreSQL schema; test harness bypasses them, so tables not represented by SQLAlchemy models would be absent under SQLite.
- Redis/Qdrant/docker services are not part of pytest setup; tests expect pure SQL operations.
- `backend/tests/test_contexts_write.py` overrides `app.dependency_overrides[get_db]` with its own SQLite engine and drops tables at module teardown, leaving subsequent tests pointing to an engine with missing schema (resolved by reusing shared fixtures).

## Assumptions / Open Questions
- Should tests use ephemeral Postgres via docker-compose or embedded SQLite file? (performance vs parity)
- Are legacy tables (e.g., `auth_user`) still required, or can they be migrated to SQLAlchemy models/migrations?
- CI environment expectations for database availability.

## Sub-agent Findings
- _Pending_

## Risks
- Introducing heavier DB setup could slow local test runs.
- Schema divergence if Alembic migrations do not faithfully recreate existing production tables.

## Next
- Inspect test fixtures and current database setup to pinpoint missing schema bootstrap steps.
