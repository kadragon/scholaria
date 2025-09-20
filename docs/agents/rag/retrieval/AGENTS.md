# RAG Retrieval Pipeline - Agent Knowledge Base

## Intent

Complete RAG pipeline: embedding → vector search → reranking → LLM generation.

## Constraints

- **TDD Required**: Red → Green → Refactor cycle
- **Service Isolation**: Independently testable services
- **Mock Testing**: External API dependencies mocked
- **Type Safety**: mypy compliance

## Context

### Services
1. **EmbeddingService**: OpenAI text-embedding-3-small
2. **QdrantService**: Vector search with topic filtering
3. **RerankingService**: BGE reranker for relevance
4. **RAGService**: Pipeline orchestration with GPT-4o-mini

### Flow
```
Query → Embedding → Vector Search → Rerank → LLM → Answer
```

## Changelog

### Core Pipeline
- TDD test suite (35 tests) for all retrieval services
- EmbeddingService with batch support, QdrantService with topic filtering
- RerankingService (BGE), RAGService with LLM orchestration
- Error handling and graceful degradation

### Configuration
- Vector dimension: 1536, Search limit: 10, Rerank top-k: 5
- GPT-4o-mini (temp: 0.3, max tokens: 1000)
- Batch processing, vector caching, model loading optimization

### Usage Monitoring
- OpenAIUsageMonitor with real-time tracking
- Cost calculation, rate limiting detection
- Management command for usage reporting
- Optimization recommendations
