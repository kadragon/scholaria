# RAG App - Agent Knowledge Base

## Intent
Django app for Retrieval-Augmented Generation system with Topic, Context, and ContextItem models.

## Constraints
- **TDD Required**: All model development follows Red → Green → Refactor cycle
- **Test Structure**: Tests organized in `/tests/` directory, not single `tests.py` file
- **Model Validation**: Custom `clean()` methods for business logic validation
- **ForeignKey Validation**: Use `field_id` checks instead of direct field access in validation
- **Type Safety**: All models have proper type annotations and pass mypy strict mode

## Context
### Model Architecture
- **Topic**: Course subjects with system prompts for LLM context
- **Context**: Document containers (PDF, FAQ, MARKDOWN types)
- **ContextItem**: Individual content pieces with file references and metadata

### Key Relationships
- Context → ContextItem (1:N via ForeignKey with CASCADE delete)
- Future: Topic ↔ Context (N:N mapping planned)

### Testing Patterns
```python
# Standard model test structure
class ModelNameTest(TestCase):
    def setUp(self):
        # Create required related objects

    def test_creation_with_required_fields(self):
        # Test basic object creation

    def test_field_required(self):
        # Test validation for each required field

    def test_string_representation(self):
        # Test __str__ method

    def test_field_max_length(self):
        # Test field constraints
```

### Django Patterns
- **Choices**: Use tuple choices for enum-like fields
- **JSONField**: For flexible metadata storage (PostgreSQL native)
- **Ordering**: Default ordering in Meta class
- **Related Names**: Descriptive related_name for reverse relationships

## Changelog
### 2025-09-18: Core Models Implementation
- ✅ Refactored test structure from single `tests.py` to `/tests/test_models.py`
- ✅ Implemented Context model with PDF/FAQ/MARKDOWN type choices
- ✅ Implemented ContextItem model with ForeignKey to Context
- ✅ Added JSONField for flexible metadata storage
- ✅ All 23 tests passing with proper TDD cycle
- ✅ Created migration 0002 for new models
- ✅ Fixed ForeignKey validation using `context_id` instead of `context`

### Next Steps
- Topic-Context N:N mapping implementation
- Admin interface with file upload integration
- Document ingestion pipeline
