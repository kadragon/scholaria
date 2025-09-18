# Scholaria Project Root - Agent Knowledge Base

## Intent
School-integrated RAG (Retrieval-Augmented Generation) system for question-answering with document context.

## Constraints
- **TDD Mandatory**: All development follows Red → Green → Refactor cycle
- **Code Quality**: Must pass ruff linting and mypy type checking before commits
- **Test Organization**: Use `/tests/` directories, not single `tests.py` files
- **Docker Development**: All services containerized for consistent environments
- **PostgreSQL Required**: JSONField and full-text search capabilities needed

## Context
### Development Workflow
```bash
# Quality checks before any commit
uv run ruff check . && uv run mypy . && uv run python manage.py test --settings=core.test_settings

# Development server
uv run python manage.py runserver

# Docker services
docker-compose up -d
```

### Project Architecture
- **Django Backend**: RAG app with Topic/Context/ContextItem models
- **Vector Store**: Qdrant for document embeddings
- **File Storage**: MinIO for document files
- **Cache/Queue**: Redis for Celery background tasks
- **Database**: PostgreSQL for structured data

### Folder-Specific Knowledge
- `/rag/`: Core Django app with models, tests in organized structure
- `/docs/tasks.md`: Comprehensive TODO tracking with progress metrics
- Each folder maintains its own `AGENTS.md` for context-specific knowledge

## Changelog
### 2025-09-18: Core Models Foundation
- ✅ Implemented TDD workflow for Context and ContextItem models
- ✅ Refactored test structure across project (moved to `/tests/` dirs)
- ✅ Established code quality pipeline (ruff + mypy)
- ✅ Created database migrations for new models
- ✅ All 23 tests passing with proper validation

### Development Standards Established
- **Test Structure**: Organized `/tests/` directories with specific test files
- **Model Patterns**: Proper validation, string representation, and ordering
- **Django Best Practices**: ForeignKey relationships, JSONField usage, proper Meta classes
- **Type Safety**: Full mypy compliance with strict mode

### Next Phase Ready
- Topic-Context N:N relationship mapping
- Admin interface implementation
- Document ingestion pipeline with Celery
