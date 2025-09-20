# Scholaria Project Root - Agent Knowledge Base

## Intent

School-integrated RAG system for Q&A with document context.

## Constraints

- **TDD Mandatory**: Red → Green → Refactor cycle
- **Code Quality**: Pass ruff + mypy before commits
- **Test Organization**: Use `/tests/` directories
- **Docker Required**: All services containerized
- **PostgreSQL**: JSONField and full-text search support
- **Pytest Parallelism**: `-n=auto` default, keep tests parallel-safe

## Context

### Architecture
- Django Backend + Qdrant vectors + MinIO files + Redis cache + PostgreSQL

### Quality Workflow
```bash
uv run ruff check . && uv run mypy . && uv run python manage.py test
uv run python manage.py runserver
docker-compose up -d
```

## Changelog

### Core Development Patterns
- **Test Structure**: Organized `/tests/` directories, TDD cycle mandatory
- **Model Patterns**: Proper validation, ForeignKey relationships, JSONField usage
- **Code Quality**: ruff + mypy compliance, parallel-safe tests
- **Architecture**: Django + Qdrant + MinIO + Redis + PostgreSQL stack

### Key Implementations
- **Models**: Topic, Context, ContextItem with N:N relationships
- **Ingestion**: Celery tasks for PDF/Markdown/FAQ processing with smart chunking
- **Retrieval**: Full RAG pipeline (embeddings → vector search → reranking → LLM)
- **API**: REST endpoints with OpenAPI documentation
- **Admin**: Django admin with bulk operations
- **Web UI**: Topic selection and Q&A interface
- **Documentation**: Complete deployment, admin, and user guides with TDD validation

### Production Ready
- Docker Compose deployment with all services
- Comprehensive documentation suite
- Security validation and file upload handling
- Performance benchmarks and monitoring
- End-to-end integration testing
