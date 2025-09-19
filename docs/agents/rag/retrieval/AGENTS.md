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

### 2025-09-19: OpenAI API Usage Monitoring Implementation

- ✅ Created comprehensive TDD test suite for API usage monitoring (5 tests)
- ✅ Implemented OpenAIUsageMonitor with real-time tracking capabilities
- ✅ Integrated monitoring into EmbeddingService and RAGService
- ✅ Added usage tracking for embeddings and chat completions
- ✅ Implemented cost calculation with current OpenAI pricing
- ✅ Created optimization recommendation engine
- ✅ Added rate limiting detection and prevention
- ✅ Created Django management command for usage reporting
- ✅ All monitoring tests passing with comprehensive coverage

### OpenAI Usage Monitoring Features

**Real-time Tracking:**
- Embeddings API: Token usage, model distribution, call frequency
- Chat Completions API: Prompt/completion tokens, model usage, response costs
- Request timestamps for rate limiting detection

**Cost Analysis:**
- Real-time cost calculation based on current OpenAI pricing
- Cost breakdown by API type (embeddings vs chat completions)
- Model-specific cost attribution and optimization

**Optimization Engine:**
- Automatic recommendations based on usage patterns
- Caching strategy suggestions for high-volume usage
- Token optimization recommendations for prompt efficiency
- Batch processing suggestions for embedding generation

**Rate Limiting Protection:**
- Real-time monitoring of request frequency
- Proactive warnings before hitting rate limits
- Historical request pattern analysis

### Management Command Usage

```bash
# Generate text report
python manage.py openai_usage_report

# Generate JSON report
python manage.py openai_usage_report --format json

# Generate report and reset metrics
python manage.py openai_usage_report --reset
```

### Performance Benefits

- **Cost Visibility**: Real-time cost tracking prevents unexpected API bills
- **Optimization Guidance**: Automated recommendations reduce API usage
- **Rate Limit Prevention**: Proactive monitoring prevents service disruptions
- **Usage Insights**: Detailed metrics enable informed optimization decisions

### Implementation Details

- **Cache-based Storage**: Uses Django cache for metrics persistence (1-hour TTL)
- **Non-blocking Integration**: Monitoring adds minimal overhead to API calls
- **Fallback Handling**: Token estimation when usage data unavailable
- **Multi-model Support**: Tracks usage across different OpenAI models

### Next Steps

- Monitor real-world usage patterns and optimize recommendations
- Add alerting for cost thresholds and rate limit approaches
- Implement historical usage trending and analytics
- Consider integration with external monitoring systems
