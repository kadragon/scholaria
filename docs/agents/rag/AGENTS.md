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
- **Chunk Tracking**: `Context.chunk_count` is recomputed via signals whenever `ContextItem` rows change — update signals if ingestion paths bypass standard create/delete.

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

### Production Features (MVP COMPLETE)
- ✅ Docker integration, performance benchmarks
- ✅ Security validation, error handling
- ✅ Rate limiting, usage monitoring
- ✅ Complete admin interface with context management
- ✅ PDF (Docling), Markdown, FAQ processing pipelines

### Context Enhancement

- Two-phase FAQ creation process implemented
- Q&A pair management interface in Context admin
- Context admin relies on `get_inline_instances` with a default inline list to keep ContextItem inline available while swapping FAQ/Markdown specific inlines per context type
- Type-specific workflows for PDF, FAQ and Markdown contexts
- FAQ-specific inline editor for Q&A pairs
- Markdown direct editing with smart chunking by sections
- Markdown-specific admin interface with chunk preview
- FAQ Q&A pairs use standard Django inline deletion (select item and save to delete)
- Context admin skips inlines on initial creation and defaults missing processing status to `PENDING` to support programmatic form posts.
- ContextItem admin stays registered (even if hidden in navigation) so `/admin/rag/contextitem/` endpoints remain available for automated workflows.
