# RAG App - Agent Knowledge Base

## Intent

Django RAG app with Topic, Context, and ContextItem models.

## Constraints

- **TDD Required**: Red → Green → Refactor cycle
- **Test Structure**: Use `/tests/` directory
- **ForeignKey Validation**: Use `field_id` checks in `clean()` methods
- **Type Safety**: mypy strict mode compliance

## Context

### Models
- **Topic**: Course subjects with system prompts
- **Context**: Document containers (PDF/FAQ/MARKDOWN)
- **ContextItem**: Content pieces with file references and metadata
- **Relationships**: Context → ContextItem (1:N), Topic ↔ Context (N:N)

### Django Patterns
- JSONField for metadata, tuple choices, default ordering, descriptive related_name

## Changelog

### Core Models
- Topic, Context, ContextItem with N:N relationships
- JSONField metadata, proper validation, cascade deletes
- Django admin with bulk operations

### Pipelines
- **Ingestion**: Celery tasks for PDF/Markdown/FAQ with smart chunking
- **Retrieval**: Full RAG (embedding → search → rerank → LLM)
- **API**: REST endpoints with rate limiting and error handling

### File Management
- MinIO storage integration with security validation
- Magic byte verification, size limits, sanitization
- Admin interface with file upload capabilities

### Testing & Quality
- TDD across all components with 200+ tests
- End-to-end integration testing
- OpenAPI documentation with Swagger UI
- 100% model coverage, 85%+ pipeline coverage

### Production Features
- Docker integration, performance benchmarks
- Security validation, error handling
- Rate limiting, usage monitoring
