---
id: AG-WORKFLOW-DEV-LOOP-001
version: 1.0.0
scope: global
status: active
supersedes: []
depends: [AG-FOUND-INTENT-001, AG-POLICY-DEV-GUARDRAILS-001]
last-updated: 2025-10-11
owner: team-admin
---
# Developer Operational Loop

## Setup & Quality Cycle
```bash
# Dependency sync
uv sync

# Static gates
uv run ruff check .
uv run ruff format --check .
uv run mypy .

# Test suite
uv run pytest backend/tests/
```

## Service Bring-Up
- Local API: `uv run uvicorn backend.main:app --reload --port 8001`.
- Frontend: `(cd frontend && npm install && npm run dev)`.
- Docker stack: `docker compose up -d`, teardown with `docker compose down -v`.
- Database migrations: `docker compose exec backend alembic upgrade head`.
- Production stack: `docker compose -f docker-compose.prod.yml up -d`.

## Observability Hooks
- Confirm OpenTelemetry exporters before enabling tracing; default sampling 100%, production target 10%.
- Access dashboards: Jaeger `http://localhost:16686`, Prometheus `http://localhost:9090`, Grafana `http://localhost:3001`.
- Keep environment flags (`OTEL_ENABLED`, `OTEL_TRACES_SAMPLER_ARG`, `PROMETHEUS_METRICS_ENABLED`) synchronized across `.env` templates and deployment manifests.
