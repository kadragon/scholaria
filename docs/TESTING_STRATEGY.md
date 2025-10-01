# Testing Strategy

## Project Philosophy

Scholaria follows **Test-Driven Development (TDD)** with the **Red → Green → Refactor** cycle and **Tidy First** principles. Every feature begins with a failing test, implements minimal code to pass, then refactors for quality.

## Testing Framework & Configuration

### Core Testing Stack

- **Pytest**: Primary test runner with fixture-driven architecture (`pytest>=8.0.0`)
- **FastAPI TestClient**: HTTP-level integration tests
- **Factory Boy**: Test data factories (`factory-boy>=3.3.0`)
- **Pytest Extensions**:
  - `pytest-anyio` for async endpoint testing
  - `pytest-celery` for ingestion worker simulations
  - `pytest-xdist` for parallel execution (opt-in)

### Test Configuration

Tests rely on pytest fixtures in `backend/tests/conftest.py`:

- **Database**: Per-worker SQLite database file automatically bootstrapped via SQLAlchemy metadata
- **Dependency Overrides**: FastAPI `get_db` / Redis clients mocked for deterministic runs
- **Password Hashing**: Passlib contexts reused to validate existing hashes
- **Caching / External Calls**: OpenAI, Docling, and Redis interactions patched within tests
- **Environment Overrides**: Tests patch `FASTAPI_ALLOWED_ORIGINS`, JWT secrets, etc., as needed

## Testing Categories

### 1. Unit Tests

**Purpose**: Test individual components in isolation
**Location**: `backend/tests/test_*.py`
**Examples**:
- `test_config.py` - Settings and dependency resolution
- `test_contexts_write.py` - Context CRUD workflows
- `test_auth.py` - JWT authentication helpers

### 2. Integration Tests

**Purpose**: Test component interactions
**Examples**:
- `test_contexts_write.py` - Ingestion pipeline interactions
- `admin/test_bulk_operations.py` - Admin API bulk workflows
- `test_app_cors.py` - CORS configuration

### 3. End-to-End Tests

**Purpose**: Test complete user workflows
**Examples**:
- `test_rag_endpoint.py` - RAG answer generation stack
- `test_history_read.py` - Topic history retrieval

### 4. Documentation Tests

**Purpose**: Validate documentation accuracy and completeness
**Pattern**: Mirror documentation structure with regression tests
**Examples**:
- `test_contributing_guidelines.py` - Validates required sections and tool references
- `test_deployment_guide.py` - Ensures deployment steps remain current
- `test_admin_user_guide.py` - Validates admin interface documentation

### 5. Performance Tests

**Purpose**: Validate system performance characteristics
**Examples**:
- `test_performance_benchmarks.py` - Query latency and throughput
- `test_golden_dataset.py` - Answer quality validation

### 6. Infrastructure Tests

**Purpose**: Test deployment and system configuration
**Examples**:
- `test_docker_integration.py` - Docker container functionality
- `test_migrations.py` - Database migration integrity

## TDD Workflow

### 1. Red Phase
```bash
# Write failing test first
uv run pytest backend/tests/test_new_feature.py
```

### 2. Green Phase
```bash
# Implement minimal code to pass
uv run pytest backend/tests/test_new_feature.py
```

### 3. Refactor Phase
```bash
# Run full test suite after refactoring
uv run pytest backend/tests -q
```

## Test Commands

### Basic Test Execution
```bash
# Run all backend tests
uv run pytest backend/tests -q

# Run specific test module
uv run pytest backend/tests/test_contexts_write.py

# Run specific test class
uv run pytest backend/tests/admin/test_bulk_operations.py::TestBulkRegenerateEmbeddings

# Run specific test method
uv run pytest backend/tests/test_contexts_write.py::TestCreateContext::test_create_pdf_context_with_file
```

### Pytest Integration
```bash
# Run with verbose output
uv run pytest backend/tests/test_contexts_write.py -v

# Run with parallel execution
uv run pytest backend/tests -n auto

# Run specific test pattern
uv run pytest -k "test_parse" -v
```

### Quality Assurance Pipeline
```bash
# Complete quality check sequence
uv run ruff check . && uv run mypy . && uv run pytest
```

## Test Organization Principles

### File Naming Convention
- Test files: `test_<module_name>.py`
- Test classes: `<ComponentName>Test`
- Test methods: `test_<behavior_description>`

### Test Structure
```python
class ComponentTest(TestCase):
    def setUp(self) -> None:
        """Set up test fixtures."""
        # Test setup code

    def test_behavior_description(self) -> None:
        """Test that component behaves correctly under specific conditions."""
        # Arrange - Set up test data
        # Act - Execute the behavior
        # Assert - Verify expected outcome
```

### Mock Usage
- Mock external dependencies (OpenAI API, file system, network calls)
- Use `unittest.mock.patch` for dependency injection
- Example: PDF parsing with Docling mocked in `test_ingestion.py`

## Testing Best Practices

### Test Quality Standards
- **Isolation**: Each test runs independently
- **Repeatability**: Tests produce consistent results
- **Fast Execution**: Optimized for developer feedback loop
- **Clear Assertions**: Descriptive failure messages
- **Comprehensive Coverage**: Test happy path, edge cases, and error conditions

### Documentation Testing
- Every major documentation file has corresponding regression tests
- Tests validate section headings, required content, and tool references
- Ensures documentation stays synchronized with code changes

### Performance Testing
- Golden dataset validation for answer quality
- Performance benchmarks for query latency
- Memory and resource usage monitoring

## Error Handling & Debugging

### Test Failures
```bash
# Run with verbose output for debugging
uv run pytest backend/tests/test_contexts_write.py --verbosity=2

# Debug specific test with pdb
uv run pytest backend/tests/test_contexts_write.py::TestCreateContext::test_create_markdown_context --pdb
```

### Common Issues
- **Migration conflicts**: Ensure test database is clean
- **External API failures**: Verify mocks are properly configured
- **Resource leaks**: Check file handles and connections are closed

## Continuous Integration

### Pre-commit Hooks
```bash
# Install pre-commit hooks
uv run pre-commit install

# Run manually
uv run pre-commit run --all-files
```

### CI Pipeline Requirements
- All tests must pass
- Code coverage targets met
- Linting and type checking clean
- Performance benchmarks within thresholds

## Success Metrics

**Current Status**: ✅ 134/134 tests passing

### Target Metrics
- **Test Coverage**: >90% line coverage
- **Test Execution Time**: <2 minutes for full suite
- **Documentation Coverage**: 100% of major guides tested
- **Performance**: <3 seconds query latency validated
- **Quality**: >80% relevant citation accuracy

## Future Enhancements

### Testing Infrastructure
- Parallel test execution optimization
- Test result caching
- Performance regression detection
- Automated golden dataset updates

### Quality Assurance
- Mutation testing for test quality validation
- Property-based testing for edge case discovery
- Visual regression testing for UI components
- Load testing for production scenarios
