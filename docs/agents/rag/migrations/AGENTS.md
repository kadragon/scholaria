# RAG Migrations - Agent Knowledge Base

## Intent

Database schema evolution tracking for RAG models with proper Django migration management.

## Constraints

- **Sequential Migrations**: Always create migrations in sequence, never skip numbers
- **Reversible Changes**: Ensure migrations can be rolled back safely
- **Data Integrity**: Foreign key constraints and indexes properly defined
- **PostgreSQL Optimized**: JSONField and other PostgreSQL-specific features used

## Context

### Migration History

- `0001_initial.py`: Topic model creation
- `0002_context_contextitem.py`: Context and ContextItem models with relationships
- `0003_topic_contexts.py`: Topic-Context ManyToMany relationship

### Key Schema Decisions

1. **JSONField Usage**: ContextItem.metadata uses native PostgreSQL JSON for flexible document metadata
2. **CASCADE Deletion**: ContextItem → Context relationship with CASCADE to maintain referential integrity
3. **ManyToMany Relationships**: Topic ↔ Context with intermediate table for flexible associations
4. **Index Strategy**: Ordering fields (name, created_at) automatically indexed by Django
5. **Field Lengths**:
   - Topic.name, Context.name: 200 chars (standard for titles)
   - ContextItem.title: 300 chars (longer document titles)
   - ContextItem.file_path: 500 chars (file system paths)

### Database Considerations

- **Test Database**: Uses SQLite for fast testing
- **Production Database**: PostgreSQL for JSON support and full-text search
- **Connection Issues**: Local PostgreSQL may not be running during development (warning expected)

## Changelog

### 2025-09-18: Core Models Schema

- ✅ Created migration 0002 for Context and ContextItem models
- ✅ Established ForeignKey relationship with proper related_name
- ✅ Configured JSONField for PostgreSQL compatibility
- ✅ Set appropriate field lengths based on use cases
- ✅ Applied proper model ordering in Meta classes

### 2025-09-18: Topic-Context Relationship

- ✅ Created migration 0003_topic_contexts for ManyToMany relationship
- ✅ Added contexts field to Topic model with reverse topics relation
- ✅ Configured blank=True for optional relationships
- ✅ Proper related_name for intuitive reverse lookups

### 2025-09-19: File Upload Enhancement

- ✅ Created migration 0004_add_uploaded_file_field
- ✅ Added uploaded_file field to ContextItem for direct file uploads
- ✅ Configured proper field attributes for file storage integration

### 2025-09-19: Migration Testing Implementation

- ✅ Created comprehensive migration rollback/forward compatibility tests
- ✅ Verified data preservation during migration cycles
- ✅ Tested migration dependency enforcement
- ✅ Validated schema integrity after migrations
- ✅ All 7 migration tests passing with 100% success rate

### Migration Files Generated

```python
# 0002_context_contextitem.py
- Create model Context (name, description, context_type, timestamps)
- Create model ContextItem (title, content, file_path, metadata, context FK)
- Proper ordering and constraints applied

# 0003_topic_contexts.py
- Add ManyToManyField contexts to Topic model
- Related name 'topics' for reverse relationship
- Blank=True for optional associations

# 0004_add_uploaded_file_field.py
- Add uploaded_file FileField to ContextItem model
- Supports direct file uploads to MinIO storage
```

### Migration Testing Strategy

Comprehensive test coverage includes:
- **Forward/Rollback Cycles**: Complete migration cycle testing
- **Data Preservation**: Verify data integrity during rollbacks
- **Dependency Validation**: Ensure proper migration order
- **Schema Validation**: Test model functionality after migrations
- **Field Constraints**: Database and model validation testing
- **JSON Field Support**: PostgreSQL-specific feature testing
