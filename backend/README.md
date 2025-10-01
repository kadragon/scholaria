# Scholaria Backend (FastAPI)

FastAPI-based backend powering the Scholaria RAG platform. Provides JWT-authenticated admin APIs, ingestion endpoints, and the public RAG question-answer workflow backed by Qdrant.

## Features

- Async RAG service with Redis caching and Qdrant vector search
- Topics, contexts, and history CRUD APIs using SQLAlchemy models
- JWT authentication reused by Refine admin frontend
- Alembic migrations aligned with production PostgreSQL schema
- Comprehensive pytest suite with strict mypy/ruff enforcement

## Local Development

```bash
# Install dependencies
uv sync --dev

# Start FastAPI server with auto-reload
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001

# Optional: start dockerized dependencies (Postgres, Redis, Qdrant)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Run tests and linters
uv run ruff check .
uv run mypy .
uv run pytest
```

The OpenAPI docs are available at `http://localhost:8001/docs`.

## Project Layout

```
backend/
├── auth/              # JWT utilities and dependencies
├── config.py          # Pydantic settings wrapper
├── dependencies/      # FastAPI dependency providers
├── models/            # SQLAlchemy models + Base/session helpers
├── retrieval/         # Embeddings, Qdrant, and monitoring services
├── routers/           # FastAPI routers (auth, rag, admin)
├── schemas/           # Pydantic response/request models
├── services/          # Application services (AsyncRAGService, etc.)
└── tests/             # Backend-focused pytest suite
```

## Data & Infrastructure

- **Database**: PostgreSQL accessed via SQLAlchemy 2.x (see `backend/models`)
- **Migrations**: Alembic (`alembic/`)
- **Cache**: Redis (async client in `backend/dependencies/redis.py`)
- **Vector Store**: Qdrant client in `backend/retrieval/qdrant.py`

## Deployment

Production builds use `Dockerfile.backend` and the `backend` service in `docker-compose.prod.yml`. Run migrations with:

```bash
docker-compose -f docker-compose.prod.yml run --rm backend uv run alembic upgrade head
```

See `docs/PRODUCTION_DOCKER.md` for the full deployment checklist.

## Testing Notes

- Tests run via `uv run pytest`; xdist is enabled in CI for parallelism.
- Guard tests ensure no Django dependencies remain in the backend package.
- Use `tests/fixtures` to share factories across modules.

For additional architectural context, review `docs/ARCHITECTURE_DECISIONS.md` and `docs/agents/AGENTS.md`.
