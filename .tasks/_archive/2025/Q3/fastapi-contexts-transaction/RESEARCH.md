# Research: FastAPI Context DB Sync

**Goal**
- Fix FastAPI contexts endpoints so they see Django-written data during tests (transaction/db synchronization).

**Scope**
- FastAPI config (`api/config.py`), SQLAlchemy engine setup (`api/models/base.py`), pytest env settings, FastAPI tests.
- Possibly Django test DB configuration.

**Related Files/Flows**
- `api/config.py` constructs `DATABASE_URL` (currently hard-coded to PostgreSQL driver).
- `api/models/base.py` builds SQLAlchemy engine with `DATABASE_URL`.
- `api/tests/test_contexts.py` uses Django ORM to create records and expects FastAPI to read them.
- `pyproject.toml` pytest env sets `DB_ENGINE=django.db.backends.sqlite3`, `DB_NAME=:memory:` for tests.

**Hypotheses**
1. SQLAlchemy still connects to PostgreSQL because `DATABASE_URL` ignores Django-style `DB_ENGINE` value.
2. For sqlite-based tests, FastAPI must use same database (likely `sqlite:///:memory:` or file) as Django to reflect data.
3. Need transaction/session management adjustments (e.g., commit/close) after DB alignment.

**Evidence**
- Running `uv run pytest api/tests/test_contexts.py -q` shows SQLAlchemy executing `select pg_catalog.version()` → PostgreSQL, while Django test DB is sqlite (per pytest env).
- Tests fail with 404 / missing context because FastAPI session queries different database.

**Assumptions / Open Questions**
- For local dev, environment likely uses PostgreSQL; fix must preserve existing connection.
- Should we support DSN override env (e.g., `DATABASE_URL`)? Already indirectly via computed property.
- Need to ensure sqlite connection when `DB_ENGINE` includes `sqlite`. handle file/in-memory cases.
- Potential need for `PRAGMA foreign_keys=ON` or connection args for sqlite? maybe optional.

**Sub-agent Findings**
- N/A

**Risks**
- Incorrect DSN mapping may break production Postgres connection.
- In-memory sqlite concurrency: SQLAlchemy separate connections may not share data unless `?check_same_thread=False` or `:memory:?cache=shared` with same connection.
- Need to ensure tests still run under pytest-xdist (multiprocessing) without DB conflicts.

**Next**
- Craft plan: adjust config to map Django `DB_ENGINE` → SQLAlchemy URL, ensure tests use same DB (maybe detect sqlite and use same file path), update session creation if sqlite memory.
