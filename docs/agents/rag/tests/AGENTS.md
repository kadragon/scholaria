# RAG Tests - Agent Knowledge Base

## Intent

TDD test suite for RAG models with comprehensive coverage.

## Constraints

- **Test Isolation**: Each class handles setup/teardown
- **Descriptive Names**: Clear behavior descriptions
- **ValidationError Testing**: Use `full_clean()` for validation
- **ForeignKey Testing**: Use `field_id` in `clean()` methods
- **Parallel Execution**: xdist-safe tests

## Context

### Structure
- `/tests/test_models.py` - Topic, Context, ContextItem tests
- Comprehensive coverage: models, admin, migrations, E2E
- Chunk counter tests ensure `Context.chunk_count` stays in sync via signals.
- Admin tests assert annotated ordering (`context_count`, `item_count`) remains query-safe.
- Documentation regression tests (e.g., `test_admin_user_guide.py`, `test_deployment_guide.py`, `test_end_user_guide.py`, `test_contributing_guidelines.py`) lock required sections and keywords for published guides.
- PDF parser tests mock Docling's `DocumentConverter` to keep ingestion behavior deterministic without network access.

### Key Patterns
- ForeignKey validation with `field_id` checks
- `setUp()` for related objects, `full_clean()` for validation
- Test categories: creation, validation, relationships, constraints

## Changelog

### Test Coverage Achievements
- **Models**: 100% coverage (Topic, Context, ContextItem relationships)
- **Admin**: 19 tests for interface and bulk operations
- **Migrations**: 7 tests for rollback/forward compatibility
- **E2E Integration**: Complete ingestion and Q&A flow testing

### Quality Validation
- Golden dataset with 12 test cases (easy/medium/hard)
- Performance benchmarks (<3 second requirement)
- Celery task error handling with retry mechanisms
- Production-ready with comprehensive test suite (200+ tests)
