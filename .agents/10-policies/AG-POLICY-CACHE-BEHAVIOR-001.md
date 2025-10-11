---
id: AG-POLICY-CACHE-BEHAVIOR-001
version: 1.0.0
scope: global
status: active
supersedes: []
depends: [AG-POLICY-DEV-GUARDRAILS-001]
last-updated: 2025-10-11
owner: team-admin
---
# Redis Cache Behavior

## Embedding Cache
- Component: `backend/retrieval/cache.EmbeddingCache`.
- Default TTL: 30 days.
- On Redis outage, disable caching logic while keeping RAG responses functional.

## Query Response Cache
- Owner: `backend/services/rag_service.AsyncRAGService`.
- Successful answers cache for 15 minutes; empty results cache for 5 minutes.
- Log cache status transitions sparingly; prioritize concise, anonymized messages.

## Operational Notes
- Configure Redis endpoints and feature flags through `REDIS_EMBEDDING_CACHE_*` environment variables.
- Include cache coverage in integration tests that exercise Redis-backed flows.
