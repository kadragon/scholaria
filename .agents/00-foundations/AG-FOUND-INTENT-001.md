---
id: AG-FOUND-INTENT-001
version: 1.0.0
scope: global
status: active
supersedes: []
depends: []
last-updated: 2025-10-11
owner: team-admin
---
# Scholaria Mission & Architectural Baseline

## Intent
- Deliver an MVP-complete, school-wide RAG platform that answers contextual questions from curated documents.
- Maintain a cohesive knowledge experience that balances search quality, observability, and operational simplicity.

## Architectural Snapshot (2025-10-10)
- **Backend**: FastAPI service using SQLAlchemy, Celery, and the AsyncOpenAI client.
- **Vector Search**: Qdrant dedicated to embedding-based retrieval.
- **Storage Pipeline**: Docling parses uploads, chunks content, and discards temporary files to avoid MinIO.
- **Caching**: Redis backs Celery, embedding caches, and short-lived RAG responses.
- **Primary Database**: PostgreSQL with JSON columns and full-text indexes.
- **AI Models**: OpenAI `text-embedding-3-large`, GPT-4o-mini, and BGE reranker.
- **Frontend**: Refine-based admin UI running via Vite (port 5173).
- **Observability Stack**: OpenTelemetry instrumentation feeding Jaeger, Prometheus, and Grafana dashboards.

## System Health Expectations
- All core services (backend, postgres, redis, qdrant, frontend, celery-worker, flower) must expose healthy endpoints.
- Observability targets: Jaeger on :16686, Prometheus on :9090, Grafana on :3001 with baseline admin/admin credentials.
- RAG cache strategy: Embed cache TTL 30 days; query cache TTL 15 minutes with empty-result TTL 5 minutes.
