# RAG Retrieval Pipeline - Agent Knowledge Base

## Intent

Complete RAG (Retrieval-Augmented Generation) query pipeline implementation with embedding generation, vector search, reranking, and answer generation.

## Constraints

- **TDD Required**: All retrieval services follow Red → Green → Refactor cycle
- **Service Isolation**: Each service (embeddings, vector search, reranking, LLM) is independently testable
- **Mock Testing**: External API dependencies are mocked for reliable testing
- **Error Handling**: Graceful degradation when services fail or no results found
- **Type Safety**: Full mypy compliance with proper service typing

## Context

### Retrieval Architecture

The RAG pipeline consists of four integrated services:

1. **EmbeddingService**: OpenAI text-embedding-3-small for query vectorization
2. **QdrantService**: Vector database for similarity search with topic filtering
3. **RerankingService**: BGE reranker for improving result relevance
4. **RAGService**: Complete pipeline orchestration with LLM answer generation

### Pipeline Flow

```
User Query → EmbeddingService → QdrantService → RerankingService → LLM → Answer
            (vectorize)       (search)        (rerank)          (generate)
```

### Key Services

#### EmbeddingService (`rag/retrieval/embeddings.py`)
- Single and batch text embedding generation
- OpenAI text-embedding-3-small model
- Input validation and error handling

#### QdrantService (`rag/retrieval/qdrant.py`)
- Vector storage and similarity search
- Topic-based filtering for scoped searches
- Collection management and metadata handling

#### RerankingService (`rag/retrieval/reranking.py`)
- BGE reranker-base cross-encoder model
- Query-document relevance scoring
- Top-k result filtering

#### RAGService (`rag/retrieval/rag.py`)
- Complete pipeline orchestration
- Context preparation for LLM
- OpenAI GPT-4o-mini for answer generation
- Source attribution and citation support

### Testing Patterns

Each service has comprehensive test coverage:
- **Validation Tests**: Input validation and error handling
- **Mock Tests**: External API interaction verification
- **Integration Tests**: Service orchestration and data flow

## Changelog

### 2025-09-18: RAG Retrieval Pipeline Implementation

- ✅ **EmbeddingService**: OpenAI text-embedding-3-small integration with batch support (8 tests)
- ✅ **QdrantService**: Vector database operations with topic filtering (10 tests)
- ✅ **RerankingService**: BGE reranker integration with top-k support (8 tests)
- ✅ **RAGService**: Complete pipeline orchestration with LLM integration (9 tests)
- ✅ **Test Coverage**: 35 new tests covering all retrieval functionality
- ✅ **Code Quality**: Full mypy type checking compliance
- ✅ **Error Handling**: Graceful degradation for missing data and API failures

### Implementation Details

- **Vector Dimension**: 1536 (OpenAI text-embedding-3-small)
- **Default Search Limit**: 10 initial results
- **Default Rerank Top-K**: 5 final results
- **LLM Model**: GPT-4o-mini for cost-effective answer generation
- **Temperature**: 0.3 for consistent, focused responses
- **Max Tokens**: 1000 for comprehensive answers

### Service Dependencies

- **OpenAI API**: Embeddings and chat completions
- **Qdrant**: Vector database for similarity search
- **Sentence Transformers**: BGE reranker model
- **Django ORM**: Topic and ContextItem model integration

### Performance Considerations

- **Batch Embeddings**: Multiple texts processed in single API call
- **Vector Caching**: Embeddings stored in Qdrant for reuse
- **Model Loading**: BGE reranker loaded once per service instance
- **Context Optimization**: Efficient text preparation for LLM

### Next Steps

- API endpoints for Q&A functionality
- Frontend integration for user queries
- Performance monitoring and optimization
- Citation extraction and reference system
