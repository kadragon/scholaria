# Plan: FastAPI Context DB Sync

**Objective**
- Ensure FastAPI SQLAlchemy layer reads the same database as Django during tests so context endpoints surface Django-created data.

**Constraints**
- Maintain PostgreSQL support for local/prod.
- Strict TDD: add failing regression test (config mapping) before fixes.
- Keep solution minimal; no broad refactors.

**Target Files & Changes**
- `api/config.py` (construct DB URL based on engine/env, support sqlite & overrides).
- `api/models/base.py` (engine options for sqlite file/shared cache).
- `core/test_settings.py`, `pyproject.toml` (align Django test DB with shared sqlite file).
- `api/tests/` (new test verifying settings mapping; adjust contexts tests if needed).
- Artifact updates (`docs/agents` as usual).

**Test / Validation Cases**
1. New unit test: `Settings.DATABASE_URL` respects sqlite env (fails now).
2. Existing `api/tests/test_contexts.py` should pass after fix.
3. Spot-check `api/tests/test_topics_poc.py` to ensure regression-free.

**Steps**
1. Add failing test covering sqlite URL construction.
2. Implement DB URL builder in `api/config.py` + update `api/models/base.py` for sqlite connect args.
3. Align Django test DB configuration (`core/test_settings.py`, pytest env) and adjust FastAPI tests if necessary.
4. Run targeted test suite (`api/tests/test_config.py`, `api/tests/test_contexts.py`, `api/tests/test_topics_poc.py`).

**Rollback**
- Revert `api/config.py`, `api/models/base.py`, and new tests.

**Review Hotspots**
- `sqlite` in-memory requires shared cache; ensure SQLAlchemy connect args align with Django test DB.
- Keep environment defaults stable for Postgres.
- Avoid leaking connections; confirm session factory still valid.

**Status**
- [x] Step 1: Test added (fails as expected)
- [x] Step 2: Config updated
- [x] Step 3: Test refinements (if needed)
- [x] Step 4: Validation run
