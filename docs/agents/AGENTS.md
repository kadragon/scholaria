# Scholaria Project Root - Agent Knowledge Base

## Intent

School-integrated RAG (Retrieval-Augmented Generation) system for question-answering with document context.

## Constraints

- **TDD Mandatory**: All development follows Red → Green → Refactor cycle
- **Code Quality**: Must pass ruff linting and mypy type checking before commits
- **Test Organization**: Use `/tests/` directories, not single `tests.py` files
- **Docker Development**: All services containerized for consistent environments
- **PostgreSQL Required**: JSONField and full-text search capabilities needed
- **Pytest Parallelism**: Default pytest run uses xdist with `-n=auto`; ensure tests are parallel-safe

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
- ✅ All 29 tests passing with proper validation
- ✅ Implemented N:N relationship between Topics and Contexts

### 2025-09-18: Admin Interface Implementation

- ✅ Created comprehensive TDD test suite for admin functionality (14 tests)
- ✅ Implemented TopicAdmin, ContextAdmin, and ContextItemAdmin
- ✅ All 43 tests passing with proper admin configurations
- ✅ Code quality maintained: ruff linting and mypy type checking passed

### 2025-09-18: Document Ingestion Pipeline Implementation

- ✅ Set up Celery app with Django integration and task discovery
- ✅ Created comprehensive TDD test suite for parsers and chunkers (18 tests)
- ✅ Implemented PDFParser using Unstructured API for text extraction
- ✅ Implemented MarkdownParser for direct file content reading
- ✅ Created intelligent TextChunker with boundary detection and overlap
- ✅ Implemented Celery tasks for document processing and ingestion
- ✅ All 61 tests passing with complete pipeline coverage
- ✅ Full mypy compliance and proper error handling

### Development Standards Established

- **Test Structure**: Organized `/tests/` directories with specific test files
- **Model Patterns**: Proper validation, string representation, and ordering
- **Django Best Practices**: ForeignKey relationships, JSONField usage, proper Meta classes
- **Type Safety**: Full mypy compliance with strict mode

### Next Phase Ready

- RAG query pipeline with Qdrant vector search and embedding generation
- API endpoints for Q&A functionality with citation support
- End-to-end integration testing and performance optimization
