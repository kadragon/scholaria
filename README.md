# Scholaria - School Integrated RAG System

✅ **MVP COMPLETE & PRODUCTION READY** - TDD-driven Retrieval-Augmented Generation system for schools.

⚠️ **MIGRATION IN PROGRESS**: Django → FastAPI migration (Phase 1)

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Docker & Docker Compose
- [uv](https://github.com/astral-sh/uv) package manager

### Development Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Run tests:**
   ```bash
   uv run python manage.py test --settings=core.test_settings
   ```

4. **Start development server:**

   **Django (existing - port 8000):**
   ```bash
   uv run python manage.py runserver
   ```

   **FastAPI (new - port 8001):**
   ```bash
   uv run uvicorn api.main:app --reload --port 8001
   ```

   Access:
   - Django Admin: http://localhost:8000/admin
   - FastAPI Docs: http://localhost:8001/docs
   - FastAPI API: http://localhost:8001/api/topics

## 🛠️ Development Commands

### Code Quality
```bash
# Lint and format code
uv run ruff check --fix .
uv run ruff format .

# Type checking
uv run mypy .

# Run all checks
uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run python manage.py test --settings=core.test_settings
```

### Testing
```bash
# Quick tests (248 tests, ~1-2 minutes) - for daily development
./scripts/test-fast.sh
# OR: uv run pytest -m "not slow"

# Unit tests only (fastest, core models/views/admin)
./scripts/test-unit.sh

# Slow tests (33 tests, includes integration/performance/migrations)
./scripts/test-slow.sh
# OR: uv run pytest -m "slow"

# All tests (281 total)
uv run pytest

# Django test runner (legacy)
uv run python manage.py test --settings=core.test_settings
```

### Database
```bash
# Make migrations
uv run python manage.py makemigrations

# Apply migrations
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser
```

### Pre-commit
```bash
# Install pre-commit hooks
uv run pre-commit install
uv run pre-commit install --hook-type pre-push

# Run pre-commit on all files
uv run pre-commit run --all-files
```

## ✅ Project Status

**134 tests passing | All core functionality implemented**

- ✅ Complete admin interface for content management
- ✅ Full ingestion pipeline with PDF/Markdown/FAQ support
- ✅ Vector search and RAG API endpoints
- ✅ Topic and Context models with CRUD operations
- ✅ Production Docker deployment ready

See [tasks.md](docs/agents/tasks.md) for detailed progress tracking.

## 🏗️ Architecture

- **Backend**: Django + Django Admin + DRF
- **Database**: PostgreSQL + Qdrant (vector DB)
- **Queue**: Celery + Redis
- **Storage**: MinIO (S3-compatible)
- **Parsing**: Docling for PDF processing
- **AI**: OpenAI GPT + BGE Reranker

## Cost-Aware Caching

- **Embedding cache**: `LLAMAINDEX_CACHE_ENABLED=true` persists OpenAI embeddings via LlamaIndex in `storage/llamaindex_cache/embedding_cache.json`. Override the directory with `LLAMAINDEX_CACHE_DIR` if you need a different location.
- **Namespacing**: keep test runs isolated with `LLAMAINDEX_CACHE_NAMESPACE`; the default is `scholaria-default`.
- **Integration tests**: export a real `OPENAI_API_KEY` when you want full end-to-end calls; leave it blank to skip the expensive RAG integration cases that rely on external APIs. Before running, execute `./scripts/qdrant-reset.sh` so the Qdrant collection matches `OPENAI_EMBEDDING_DIM` (3072 for production keys).

## 🧪 Testing Strategy

Following strict TDD principles:
1. Write failing tests first (Red)
2. Implement minimal code to pass (Green)
3. Refactor and improve (Refactor)

Current test coverage focuses on models with comprehensive validation testing.
