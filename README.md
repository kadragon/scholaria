# Scholaria - School Integrated RAG System

MVP-first, TDD-driven development of a Retrieval-Augmented Generation system for schools.

## =� Quick Start

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
   ```bash
   uv run python manage.py runserver
   ```

## =� Development Commands

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
# Run all tests
uv run python manage.py test --settings=core.test_settings

# Run specific test
uv run python manage.py test rag.tests.TopicModelTest --settings=core.test_settings
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

## =� Project Status

-  **Foundation Complete**: uv, Docker, Django, code quality tools
-  **Topic Model**: Fully tested and implemented
- =� **Next**: Context and ContextItem models
- =� **Remaining**: Admin interface, ingestion pipeline, RAG API

See [TODO.md](docs/TODO.md) for detailed progress tracking.

## <� Architecture

- **Backend**: Django + Django Admin + DRF
- **Database**: PostgreSQL + Qdrant (vector DB)
- **Queue**: Celery + Redis
- **Storage**: MinIO (S3-compatible)
- **Parsing**: Unstructured API
- **AI**: OpenAI GPT + BGE Reranker

## >� Testing Strategy

Following strict TDD principles:
1. Write failing tests first (Red)
2. Implement minimal code to pass (Green)
3. Refactor and improve (Refactor)

Current test coverage focuses on models with comprehensive validation testing.
