# RAG Migrations - Agent Knowledge Base

## Intent

Database schema evolution for RAG models.

## Constraints

- **Sequential Migrations**: Create in sequence, never skip numbers
- **Reversible Changes**: Ensure rollback safety
- **PostgreSQL Features**: JSONField and full-text search

## Context

### Migration Files
- `0001_initial.py`: Topic model
- `0002_context_contextitem.py`: Context + ContextItem with relationships
- `0003_topic_contexts.py`: Topic-Context ManyToMany
- `0004_add_uploaded_file_field.py`: File upload support

### Schema Decisions
- JSONField for ContextItem.metadata (PostgreSQL native)
- CASCADE deletion: ContextItem → Context
- Field lengths: Topic/Context names (200), ContextItem title (300), file_path (500)

## Changelog

### Migration Evolution
- Core models with JSONField and proper relationships
- Topic-Context ManyToMany mapping
- File upload support for ContextItem
- Comprehensive rollback/forward testing

### Testing Strategy
- Migration cycle validation with data preservation
- Dependency enforcement and schema integrity
- PostgreSQL-specific feature testing
