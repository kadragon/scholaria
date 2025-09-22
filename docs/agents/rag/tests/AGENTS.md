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
- `/tests/test_local_docker.py` guards the local Docker compose artefacts and expected web service wiring.

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
- Performance benchmarks: single worker <1s, parallel <5s (accounts for pytest-xdist overhead)
- Celery task error handling with retry mechanisms
- Production-ready with comprehensive test suite (200+ tests)
- Added regression for markdown ingestion when Celery request metadata (`id`/`called_directly`/`eta`) is missing to cover direct task invocation.

### Performance Testing Insights
- Celery tasks use `bulk_create` for optimal database performance (1000 items in ~0.2s)
- Test environment detection via `PYTEST_XDIST_WORKER` environment variable
- Parallel test execution adds ~8-10x overhead due to worker coordination
- Performance assertions differentiate between single/parallel execution contexts

### Testing Patterns for Monitoring Systems
- **Mock Monitoring Classes**: Always mock `OpenAIUsageMonitor` in retrieval tests to prevent cache serialization errors with MagicMock objects
- **Cache Avoidance**: MagicMock objects cannot be pickled by Django's cache system (Redis backend), causing test failures
- **Pattern**: Use `@patch("rag.retrieval.embeddings.OpenAIUsageMonitor")` and return a mocked instance to bypass cache operations

### Service Mocking in E2E Tests
- **Service Initialization**: Initialize services within mock context to ensure patches are applied correctly
- **Correct Patch Paths**: Use import-path-based patches:
  - EmbeddingService: `@patch("rag.retrieval.embeddings.openai.OpenAI")`
  - QdrantService: `@patch("rag.retrieval.qdrant.qdrant_client.QdrantClient")`
- **Alternative Pattern**: Use `@patch.object(ServiceClass, 'method_name')` for simpler, more reliable mocking
- **Embedding Dimensions**: Test embedding dimensions must match actual service configuration (text-embedding-3-small: 1536, text-embedding-3-large: 3072)
- **Operation ID Format**: Mock Qdrant responses must include `operation_id` attribute that returns string values
