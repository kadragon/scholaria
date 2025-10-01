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
- MinIO (9000-9001); Docling runs in-process within the FastAPI backend container (no external service)

### Development Setup
- `docker-compose.dev.yml` extends the base compose file to run the FastAPI `backend` container with live reload.
- `Dockerfile.dev` serves autoreloading `uvicorn backend.main:app` with a mounted project volume for hot reloading.

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
- All core services run together in Docker Compose (PostgreSQL, Redis, Qdrant, MinIO)
- Data flows correctly between PostgreSQL and Qdrant
- FastAPI Redis dependency integrates with Redis
- Production deployment ready
