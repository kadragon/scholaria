# Research: FastAPI Read-Only API

**Goal**
- Advance Phase 2 by covering remaining read-only endpoints (e.g., question history) with FastAPI while keeping parity with existing Django responses.

**Scope**
- FastAPI routers (`api/routers`), schemas, services for read endpoints.
- Django reference views and serializers (`rag/views.py`) and associated tests (`rag/tests/test_history_api.py`).
- FastAPI tests (`api/tests/`) for regression coverage.

**Related Files/Flows**
- `api/routers/topics.py`, `api/routers/contexts.py`: existing read-only endpoints.
- `api/schemas/topic.py`, `api/schemas/context.py`: Pydantic models mirroring Django serializers.
- `rag/views.py`: source-of-truth for history, favorites, topics, contexts.
- `rag/tests/test_history_api.py`: expected payload/behaviour for history endpoints.

**Hypotheses**
1. Question history GET endpoint (`/api/history`) is missing on FastAPI side; implementing it unlocks parity for saved conversations.
2. We can reuse Django ORM via SQLAlchemy session to read `question_history` entries using shared DB config (already aligned via previous task).
3. TDD via FastAPI TestClient referencing Django-created data will enforce parity.

**Evidence**
- No `history` router under `api/routers/`; search returns only Django tests.
- Phase 2 plan explicitly lists history endpoint as part of read-only migration.
- Recent DB sync work ensures tests can share sqlite file, reducing integration friction.

**Assumptions / Open Questions**
- Response payload should include keys `history` (list of question dicts) similar to Django (`rag/views.py` ? need to confirm structure).
- Filtering fields: Django endpoint uses `topic_id` and `session_id` query params; need to mirror.
- Should FastAPI route live under `/api/history` (per plan) vs original Django path `api_question_history`? adopt plan naming.

**Sub-agent Findings**
- N/A

**Risks**
- Divergent payload shape could break FE integration; must inspect Django serializer to replicate.
- Query parameter validation (string vs int) needs Pydantic model to ensure error handling.

**Next**
- Draft plan: tests first (history GET), implement router/service, validate.
