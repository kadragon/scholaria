# Spec Delta: Celery Worker Docker Fix

## Acceptance Criteria
1. `docker compose up celery-worker` on macOS (Apple Silicon) and Linux starts the container without crashing and shows the worker boot banner within 15 seconds.
2. `docker compose run --rm celery-worker -- celery -A celery_app inspect ping` exits with status code `0`, confirming the isolated uv environment exposes the Celery CLI.
3. Playwright tests that were previously skipped due to missing RAG responses remain eligible to run (no new skip markers tied to Celery startup failures).
4. The production stack (`docker-compose.prod.yml`) continues to use the existing command and remains unaffected by the development fix.

## Non-Goals
- No change to the backend service hot-reload workflow.
- No refactor of Playwright specs beyond removing Celery-related skip guards once the worker is healthy.
