# Docker Integration - Agent Knowledge Base

## Intent

Docker Compose integration testing for containerized RAG services.

## Constraints

- **TDD Methodology**: Red → Green → Refactor cycle
- **Environment Isolation**: Run with `DOCKER_INTEGRATION_TESTS=true`
- **Performance**: All services respond within time limits
- **Graceful Degradation**: Handle unavailable services

## Context

### Services
- PostgreSQL (port 5432), Redis (6379), Qdrant (6333-6334)
- MinIO (9000-9001), Unstructured API (8000)

### Test Coverage
- Service connectivity, data persistence, cross-service consistency
- Performance benchmarks, error handling

## Changelog

### Integration Testing
- TDD approach with service availability detection
- Cross-service data consistency validation
- Performance benchmarks (Redis <1s, Qdrant <2s, PostgreSQL sub-second)
- Automated scripts for Docker testing

### Validation Results
- All core services run together in Docker Compose
- Data flows correctly between PostgreSQL and Qdrant
- Django cache integrates with Redis
- Production deployment ready
