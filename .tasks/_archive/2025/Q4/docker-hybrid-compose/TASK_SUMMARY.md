Goal: Enable Docker hybrid runtime (Django 8000 + FastAPI 8001) for Phase 1 migration work.
Key Changes:
- Added compose regression test (`rag/tests/test_docker_fastapi_service.py`).
- Introduced FastAPI dev entrypoint and service in `docker-compose.dev.yml`.
- Documented Docker hybrid workflow in `README.md` and `api/README.md`.
Tests: `uv run pytest rag/tests/test_docker_fastapi_service.py api/tests/test_topics_poc.py -q` (pass).
Notes: FastAPI service now available via `docker compose -f docker-compose.yml -f docker-compose.dev.yml up web fastapi` with optional `FASTAPI_PORT` override.
