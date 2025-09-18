# RAG Tests - Agent Knowledge Base

## Intent
TDD test suite for RAG models ensuring comprehensive coverage and Django best practices.

## Constraints
- **Test Isolation**: Each test class handles its own setup/teardown
- **Descriptive Names**: Test method names clearly describe expected behavior
- **ValidationError Testing**: Use `full_clean()` for model validation tests
- **ForeignKey Testing**: Create required related objects in `setUp()` method
- **Import Organization**: Follow ruff import sorting (django, external, local)

## Context
### Test File Structure
```
/tests/
├── __init__.py
├── test_models.py      # Model tests (Topic, Context, ContextItem)
└── AGENTS.md          # This file
```

### Testing Patterns Discovered
1. **ForeignKey Validation**: Django's ForeignKey fields raise `RelatedObjectDoesNotExist` when accessed on unsaved objects without the related object. Solution: validate using `field_id` instead of `field` in model's `clean()` method.

2. **Test Data Setup**: Use `setUp()` method for creating required related objects that multiple tests depend on.

3. **Validation Testing**: Always use `full_clean()` to trigger model validation, not just `save()`.

### Coverage Status
- **Topic Model**: 6 tests ✅
- **Context Model**: 8 tests ✅
- **ContextItem Model**: 9 tests ✅
- **Total**: 23 tests passing

### Test Categories per Model
- Creation with required fields
- Individual field validation (required checks)
- String representation (`__str__` method)
- Field constraints (max_length, choices)
- Ordering behavior
- Relationship integrity

## Changelog
### 2025-09-18: Test Structure Refactoring
- ✅ Migrated from single `tests.py` to organized `/tests/` directory
- ✅ Implemented comprehensive test coverage for all models
- ✅ Fixed ForeignKey validation testing pattern
- ✅ All tests passing with proper Django test database setup
- ✅ Automated import sorting with ruff
