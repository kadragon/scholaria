---
id: AG-FOUND-DOCKER-STACK-001
version: 1.0.0
scope: folder:docker
status: active
supersedes: []
depends: [AG-FOUND-INTENT-001]
last-updated: 2025-10-11
owner: platform-team
---
# Docker Stack Purpose

## Intent
- Validate and operate the Scholaria RAG platform through a unified `docker compose` stack.
- Provide a reproducible integration surface covering backend, data services, and observability tooling.

## Service Inventory
- `backend`: FastAPI container launched via `scripts/docker/dev-entrypoint.sh`.
- `postgres`, `redis`, `qdrant`: core data layer.
- `frontend`: Refine/Vite admin UI (port 5173).
- `celery-worker`, `flower`: async job execution and monitoring.
- Production overlay (`docker-compose.prod.yml`) adds an nginx reverse proxy.
