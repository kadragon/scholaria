# Plan: FastAPI Read-Only API

**Objective**
- Implement FastAPI question history read endpoint(s) to match Django API responses, moving Phase 2 forward.

**Constraints**
- Strict TDD (write failing FastAPI test first).
- Match Django payload structure and filtering semantics.
- Keep change set focused (read endpoint only; write/favorite toggles deferred).

**Target Files & Changes**
- `api/routers/history.py` (new) with GET `/api/history` implementation.
- `api/schemas/history.py` or augment existing schema module.
- `api/tests/test_history_read.py` (new) covering query scenarios.
- `api/main.py` to include new router.
- Documentation (e.g., `api/README.md`) if needed to mention endpoint.
- Task artifacts updates.

**Test / Validation Cases**
1. FastAPI test: GET `/api/history` returns list filtered by topic + session (fails initially).
2. Edge test: missing query params -> 422 or 400 consistent with expectation.
3. Regression: `api/tests/test_topics_poc.py` still passes.

**Steps**
1. Add failing FastAPI test for `/api/history` (happy path & missing params as needed).
2. Implement router + schema + service logic to satisfy test (reuse SQLAlchemy session).
3. Update docs (api README) for new endpoint.
4. Run targeted suite (`api/tests/test_history_read.py`, `api/tests/test_topics_poc.py`).

**Rollback**
- Revert new router/test files, revert `api/main.py` and schema changes.

**Review Hotspots**
- Ensure timezone formatting uses existing helper (`to_local_iso`).
- Query param validation via dependency or `Depends` using Pydantic model.
- Efficient query (order by created desc? check Django view).

**Status**
- [x] Step 1: Test added
- [x] Step 2: Implementation
- [x] Step 3: Docs updated
- [x] Step 4: Validation run
