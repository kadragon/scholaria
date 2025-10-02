Goal: Deliver FastAPI read-only question history endpoint matching Django behaviour.
Key Changes:
- Added SQLAlchemy `QuestionHistory` model and Pydantic schema for history payloads.
- Introduced `/api/history` router with topic/session filtering plus shared sqlite test DB usage.
- Documented endpoint in `api/README.md` and validated via `uv run pytest api/tests/test_history_read.py api/tests/test_topics_poc.py -q`.
