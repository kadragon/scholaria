# RAG Tests - Agent Knowledge Base

## Intent

TDD test suite for RAG models ensuring comprehensive coverage and Django best practices.

## Constraints

- **Test Isolation**: Each test class handles its own setup/teardown
- **Descriptive Names**: Test method names clearly describe expected behavior
- **ValidationError Testing**: Use `full_clean()` for model validation tests
- **ForeignKey Testing**: Create required related objects in `setUp()` method
- **Import Organization**: Follow ruff import sorting (django, external, local)
- **Parallel Execution**: Pytest runs with xdist (`-n=auto`); keep tests parallel-safe

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
- **Topic-Context Relationship**: 6 tests ✅
- **Admin Interface**: 19 tests ✅
- **Bulk Operations**: 12 tests ✅
- **Migration Compatibility**: 7 tests ✅
- **Total**: 67 tests passing

### Test Categories per Model

- Creation with required fields
- Individual field validation (required checks)
- String representation (`__str__` method)
- Field constraints (max_length, choices)
- Ordering behavior
- Relationship integrity (ManyToMany operations)

## Changelog

### 2025-09-18: Test Structure Refactoring

- ✅ Migrated from single `tests.py` to organized `/tests/` directory
- ✅ Implemented comprehensive test coverage for all models
- ✅ Fixed ForeignKey validation testing pattern
- ✅ All tests passing with proper Django test database setup
- ✅ Automated import sorting with ruff

### 2025-09-18: Topic-Context Relationship Tests

- ✅ Added 6 comprehensive tests for ManyToMany relationship functionality
- ✅ Tests cover add/remove operations, reverse relationships, and clear operations
- ✅ All 29 tests passing with proper validation patterns

### 2025-09-19: Admin Interface and Bulk Operations

- ✅ Implemented comprehensive admin interface tests (19 tests)
- ✅ Added bulk operations testing suite (12 tests)
- ✅ Created migration compatibility tests (7 tests)
- ✅ All admin actions and bulk functionality thoroughly tested
- ✅ Total test coverage increased to 67 tests with 100% pass rate

### 2025-09-19: Migration Testing Implementation

- ✅ Added comprehensive migration rollback/forward compatibility tests
- ✅ Verified data preservation during migration cycles
- ✅ Tested migration dependency enforcement
- ✅ All migration operations tested for reliability

### 2025-09-19: Golden Dataset Quality Validation

- ✅ Implemented comprehensive golden dataset for RAG quality validation
- ✅ Created 12 test cases covering fundamentals, algorithms, and applications
- ✅ Includes easy, medium, and hard difficulty levels for comprehensive testing
- ✅ Added keyword matching and relevance scoring algorithms
- ✅ Built performance tracking with response time measurement
- ✅ Created validation framework that can be extended for production monitoring

### 2025-09-19: Performance Benchmarks (< 3 Second Response Time)

- ✅ Implemented comprehensive performance benchmarking framework
- ✅ Created single query response time measurement (< 3 second requirement)
- ✅ Built concurrent query performance testing with ThreadPoolExecutor
- ✅ Added sustained load testing with configurable duration and request counts
- ✅ Implemented memory usage monitoring during RAG operations
- ✅ Created percentile calculations (P95, P99) for response time distribution
- ✅ Built comprehensive performance reporting with bottleneck identification
- ✅ Added Django management command for CLI benchmark execution
- ✅ All performance tests validate the < 3 second response time requirement

### 2025-09-19: Celery Task Processing and Error Handling

- ✅ Enhanced all Celery tasks with comprehensive error handling and logging
- ✅ Implemented automatic retry mechanisms for transient errors (network, timeout)
- ✅ Added input validation and parameter checking in all task functions
- ✅ Created database transaction safety with atomic operations
- ✅ Built comprehensive error handling test suite (19 tests)
- ✅ Tested file system errors, database errors, parsing failures, and chunking errors
- ✅ Implemented task monitoring and performance tracking capabilities
- ✅ Added task metadata for observability (task_id, timestamps, processing stats)
- ✅ Enhanced bulk operations for efficiency and memory management
- ✅ Created proper exception chaining for better debugging
- ✅ All Celery tasks now production-ready with enterprise-grade error handling
