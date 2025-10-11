---
id: AG-WORKFLOW-RAG-TESTS-001
version: 1.0.0
scope: global
status: active
supersedes: []
depends: [AG-WORKFLOW-FASTAPI-OPS-001]
last-updated: 2025-10-11
owner: team-admin
---
# RAG Endpoint Validation

## Test Coverage
- Canonical suites: `backend/tests/test_rag_endpoint.py` and `backend/tests/test_rag_streaming.py`.
- Cover success, validation error, and failure paths with Redis/Qdrant interactions mocked.

## Deterministic Runs
- Disable network calls through fixtures; rely on recorded embeddings and reranker outputs.
- When running inside Docker, set `DOCKER_INTEGRATION_TESTS=true` to enable full-stack assertions.

## Performance Expectations
- Redis ping must be under 1 second; Qdrant search latency stays below 2 seconds during integration tests.
- Log slow queries with context (topic id, document count) while redacting user identifiers.
