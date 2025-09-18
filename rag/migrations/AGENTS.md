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

### Key Schema Decisions
1. **JSONField Usage**: ContextItem.metadata uses native PostgreSQL JSON for flexible document metadata
2. **CASCADE Deletion**: ContextItem → Context relationship with CASCADE to maintain referential integrity
3. **Index Strategy**: Ordering fields (name, created_at) automatically indexed by Django
4. **Field Lengths**:
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

### Migration Files Generated
```python
# 0002_context_contextitem.py
- Create model Context (name, description, context_type, timestamps)
- Create model ContextItem (title, content, file_path, metadata, context FK)
- Proper ordering and constraints applied
```
