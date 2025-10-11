---
id: AG-POLICY-DOCKER-CONSTRAINTS-001
version: 1.0.0
scope: folder:docker
status: active
supersedes: []
depends: [AG-FOUND-DOCKER-STACK-001]
last-updated: 2025-10-11
owner: platform-team
---
# Docker Environment Constraints

## Methodology
- Uphold TDD cycles even when running in containers: fail a test before implementing fixes.
- Isolate integration tests by setting `DOCKER_INTEGRATION_TESTS=true` to differentiate from local-fast runs.

## Performance & Resilience
- Ensure backend (8001), Qdrant (6333), PostgreSQL (5432), Redis (6379), and frontend (5173) respond before greenlighting a build.
- Implement clear rollback commands for each service; document failure modes in task notes.

## Observability
- Expose container health and logs quickly; Flower must reflect Celery status, and Grafana dashboards should pull Prometheus metrics without manual wiring.
