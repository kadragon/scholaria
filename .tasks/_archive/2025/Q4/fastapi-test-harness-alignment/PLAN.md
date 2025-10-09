# Plan: FastAPI Test Harness Alignment

## Objective
- Ensure backend pytest suite runs green using a FastAPI-native database setup (no Django dependencies).

## Constraints
- Maintain TDD discipline: add/adjust tests before code when feasible.
- Avoid destabilizing production migrations; prefer test-only fixtures or dedicated test DB.

## Target Files & Changes
- `backend/tests/conftest.py`, fixtures for DB/session/user seeding.
- Test settings or environment: `.env.test`, pytest config, `docker-compose.yml` overrides.
- Alembic/SQL scripts for initializing `auth_user` equivalent or refactoring tests to use SQLAlchemy models.
- CI/test scripts invoking pytest.

## Test / Validation Cases
- `uv run pytest` completes without missing-table errors.
- Targeted admin/context tests pass (login, CRUD, bulk operations).
- Optional: smoke run for dockerized integration tests if impacted.

## Steps
1. Audit pytest fixtures and current DB initialization paths; document schema gaps.
2. Prototype DB bootstrap strategy (e.g., Alembic upgrade in-memory SQLite, or spin up Postgres fixture) and capture failing test evidence.
3. Normalize dependency overrides so all tests share centralized database engine configuration.
4. Implement schema/bootstrap fixes with minimal code changes.
5. Refactor tests to rely on SQLAlchemy models instead of Django artifacts.
6. Update scripts/docs to reference new workflow.
7. Run full pytest + lint/type checks to confirm stability.

## Rollback
- Revert fixture/migration changes via git if new approach fails; retain previous guard test ensuring no Django imports.

## Review Hotspots
- Fixtures creating admin users, context data, and session scopes.
- Alembic baseline (ensuring it covers `auth_user` or equivalent user table).

## Status
- [x] Step 1: audit fixtures and schema gaps
- [x] Step 2: prototype DB bootstrap
- [x] Step 3: normalize dependency overrides
- [x] Step 4: implement schema/bootstrap fixes
- [x] Step 5: refactor tests
- [x] Step 6: update scripts/docs
- [x] Step 7: validation
