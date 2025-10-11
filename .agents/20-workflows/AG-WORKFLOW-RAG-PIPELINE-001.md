---
id: AG-WORKFLOW-RAG-PIPELINE-001
version: 1.0.0
scope: folder:backend/retrieval
status: active
supersedes: []
depends: [AG-WORKFLOW-RAG-TESTS-001, AG-POLICY-CACHE-BEHAVIOR-001]
last-updated: 2025-10-11
owner: rag-team
---
# RAG Retrieval Pipeline Operations

## Intent
- Orchestrate embeddings, vector search, reranking, and LLM answer assembly with predictable quality.
- Keep each stage independently testable with clear mocking boundaries.

## Core Services
1. **EmbeddingService** (`backend/retrieval/embeddings.py`)
   - Uses OpenAI `text-embedding-3-large` and leverages `EmbeddingCache`.
   - Supports batch embeddings and tracks usage through `OpenAIUsageMonitor`.
2. **QdrantService** (`backend/retrieval/qdrant.py`)
   - Applies topic ID filters with 3072-dimension vectors and a default limit of 10 hits.
3. **RerankingService** (`backend/retrieval/reranking.py`)
   - Applies BGE reranker, defaulting to top 5 candidates.
4. **AsyncRAGService** (`backend/services/rag_service.py`)
   - Coordinates the full flow, caches answers for 15 minutes (empty results 5 minutes), and supports streaming responses.
5. **OpenAIUsageMonitor** (`backend/retrieval/monitoring.py`)
   - Tracks API utilization, cost projections, and rate-limit signals.

## Flow Summary
```
사용자 질문 → 임베딩 생성 → Qdrant 유사도 검색 → BGE 리랭크 → 컨텍스트 조립 → GPT-4o-mini 응답 → 답변 + 출처 반환
```

## Testing Guidelines
- Unit tests: `backend/tests/test_embedding_cache.py`, `test_rag_endpoint.py`, `test_rag_streaming.py`, `test_openai_usage_monitor_metrics.py`.
- Integration: enable `DOCKER_INTEGRATION_TESTS=true` and run under Docker to activate Redis/Qdrant/PostgreSQL dependencies.
- Mock external APIs (`openai.OpenAI`, `openai.AsyncOpenAI`, Redis, Qdrant) at the module boundary for deterministic runs.
