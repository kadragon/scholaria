---
id: AG-WORKFLOW-DOCKER-DEV-001
version: 1.0.0
scope: folder:docker
status: active
supersedes: []
depends: [AG-POLICY-DOCKER-CONSTRAINTS-001]
last-updated: 2025-10-11
owner: platform-team
---
# Docker Development Flow

## Lifecycle Commands
- Start: `docker compose up -d`.
- Stop & clean volumes: `docker compose down -v`.
- Run migrations: `docker compose exec backend uv run alembic upgrade head`.
- Production rollout: `docker compose -f docker-compose.prod.yml up -d`.

## Integration Testing
- Execute `uv run pytest backend/tests/` with containers running to capture Redis/Qdrant/Postgres dependencies.
- Use `DOCKER_INTEGRATION_TESTS=true` to enable service-aware assertions.
- Target latency benchmarks: Redis ping < 1 second, Qdrant query < 2 seconds.
