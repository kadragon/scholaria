---
id: AG-OVERRIDE-CHANGELOG-001
version: 1.0.0
scope: global
status: active
supersedes: []
depends: [AG-FOUND-INTENT-001]
last-updated: 2025-10-11
owner: team-admin
---
# Scholaria Change Log (Snapshots)

## 2025-10-10
- Test suite: 223 passed, 21 skipped, 83% coverage via `uv run pytest --disable-warnings -q`.
- Docker Compose includes backend, postgres, redis, qdrant, frontend, celery-worker, flower, jaeger, prometheus, grafana.
- Production stack uses `docker-compose.prod.yml` with nginx reverse proxy.
- `uv.lock` aligned with Docling 2.53.0, Python 3.13.5, OpenTelemetry 1.37.0.

## 2025-10-09
- Simplified Docker Compose layout to a single development file; updated service roster.
- FastAPI operations consolidated under `backend/config.Settings`; documented Docker-based startup flow.
- Redis cache policy updated: embedding cache TTL 30 days, query cache TTL 15 minutes, empty responses 5 minutes.
- Integration scripts now support both `docker compose` and `docker-compose`.

## 2025-10-01
- Converted context-topic relationship to N:N and refreshed Docling-based ingestion pipeline.
- Removed lingering Django dependencies; async services now rely on `asyncio.to_thread`.
- Hardened RAG endpoint tests with mocks and streaming coverage.
