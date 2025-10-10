# Research: OpenTelemetry Observability for RAG Pipeline

**Task ID**: observability-opentelemetry
**Date**: 2025-10-10
**Status**: Research Complete

---

## Goal

Add comprehensive observability to the RAG pipeline using OpenTelemetry, enabling real-time monitoring of:
- End-to-end request latency
- Individual component performance (embedding, vector search, reranking, LLM)
- Error rates and failures
- Token usage and costs
- Cache hit/miss ratios

---

## Current State Analysis

### Existing Monitoring Infrastructure

**Location**: `backend/retrieval/monitoring.py`

The codebase already has a custom `OpenAIUsageMonitor` class that tracks:
- Embedding API calls and token usage
- Chat completion calls and token usage (prompt, completion, total)
- Request timestamps for rate limiting detection
- Cost breakdown estimation
- Usage recommendations

**Current Integration Points**:
1. **EmbeddingService** (`backend/retrieval/embeddings.py:23,47,60`):
   - Tracks embedding API usage after each call
   - Tracks request timestamps for rate limiting

2. **AsyncRAGService** (`backend/services/rag_service.py:46,208,224,365`):
   - Instantiates `OpenAIUsageMonitor`
   - Tracks chat completion usage with token counts
   - Tracks request timestamps

### RAG Pipeline Architecture

**Flow** (`backend/services/rag_service.py:query` and `query_stream`):

1. **Embedding Generation** (line 119-121)
   - `EmbeddingService.generate_embedding(query)`
   - Synchronous, wrapped in `asyncio.to_thread()`
   - Uses OpenAI API with Redis caching

2. **Vector Search** (line 124-129)
   - `QdrantService.search_similar(query_embedding, topic_ids, limit)`
   - Synchronous, wrapped in `asyncio.to_thread()`
   - Qdrant vector DB with topic filtering

3. **Reranking** (line 143-148)
   - `RerankingService.rerank_results(query, search_results, top_k)`
   - Synchronous BGE cross-encoder model
   - Wrapped in `asyncio.to_thread()`

4. **Context Preparation** (line 151)
   - `_prepare_context(reranked_results)`
   - Pure Python string formatting

5. **LLM Answer Generation** (line 154, 192-251)
   - `_generate_answer(query, context_text)` or `_generate_answer_stream()`
   - Async OpenAI API call
   - Tracks usage via `OpenAIUsageMonitor`

### Key Observation Points

**Critical Metrics**:
- Embedding cache hit/miss ratio (Redis-based, TTL 30 days)
- Query result cache hit/miss ratio (Redis-based, TTL 15 min / 5 min for empty)
- Qdrant search latency and result count
- BGE reranking latency
- OpenAI API latency (embedding, chat completion)
- Token usage per request (prompt, completion)
- End-to-end pipeline latency
- Error rates at each stage

**Entry Points**:
- FastAPI routes: `/api/rag`, `/api/rag/stream`
- Admin analytics endpoints

---

## OpenTelemetry Integration Strategy

### Hypothesis

OpenTelemetry provides:
1. **Auto-instrumentation** for FastAPI, HTTP clients (httpx/requests), Redis
2. **Custom spans** for domain-specific operations (embedding, rerank, LLM)
3. **Metrics** for counters, histograms, gauges (token usage, cache hits)
4. **Unified exporters** to Jaeger (traces), Prometheus (metrics), and logs

### Evidence from Research

**Auto-Instrumentation Packages**:
- `opentelemetry-instrumentation-fastapi` - automatic HTTP request tracing
- `opentelemetry-instrumentation-httpx` - OpenAI client instrumentation (uses httpx)
- `opentelemetry-instrumentation-redis` - Redis cache instrumentation
- `opentelemetry-instrumentation-sqlalchemy` - Database query tracing

**Manual Instrumentation**:
- Custom spans using `tracer.start_as_current_span()`
- Span attributes for business logic (model names, token counts, cache status)
- Span events for notable occurrences (cache misses, empty results)

**Exporters**:
- **Jaeger**: OTLP exporter for distributed tracing
- **Prometheus**: Metrics exporter with pull-based scraping
- **Console**: Development/debugging exporter

### Integration Pattern

```python
# backend/observability.py (new module)
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader

def setup_observability(app):
    # Set up tracing
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint="jaeger:4317"))
    )

    # Set up metrics
    metrics.set_meter_provider(MeterProvider(metric_readers=[PrometheusMetricReader()]))

    # Auto-instrument
    FastAPIInstrumentor.instrument_app(app)
    HTTPXClientInstrumentor().instrument()
    RedisInstrumentor().instrument()
```

**Custom Spans in RAG Pipeline**:
```python
tracer = trace.get_tracer(__name__)

async def query(self, query: str, topic_ids: list[int], ...):
    with tracer.start_as_current_span("rag.query") as span:
        span.set_attribute("query.length", len(query))
        span.set_attribute("topic_ids.count", len(topic_ids))

        with tracer.start_as_current_span("rag.embedding"):
            query_embedding = await asyncio.to_thread(...)

        with tracer.start_as_current_span("rag.vector_search") as search_span:
            search_results = await asyncio.to_thread(...)
            search_span.set_attribute("results.count", len(search_results))

        with tracer.start_as_current_span("rag.rerank"):
            reranked_results = await asyncio.to_thread(...)

        with tracer.start_as_current_span("rag.llm_generation"):
            answer = await self._generate_answer(...)
```

---

## Observability Stack Design

### Components

1. **OpenTelemetry SDK** (Python instrumentation)
   - Trace collection and export
   - Metrics collection and export
   - Auto-instrumentation for FastAPI, httpx, Redis

2. **Jaeger** (Distributed Tracing UI)
   - OTLP receiver on port 4317 (gRPC)
   - UI on port 16686
   - Storage: in-memory (development) or Cassandra/Elasticsearch (production)

3. **Prometheus** (Metrics Collection)
   - Scrapes metrics from `/metrics` endpoint
   - Port 9090 (UI)
   - Stores time-series data

4. **Grafana** (Visualization Dashboard)
   - Port 3001 (avoid conflict with potential frontend on 3000)
   - Data sources: Prometheus (metrics), Jaeger (traces)
   - Pre-built dashboards for RAG pipeline

### docker-compose.yml Extension

```yaml
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC receiver
    environment:
      - COLLECTOR_OTLP_ENABLED=true

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./grafana/datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
      - ./grafana/dashboards.yml:/etc/grafana/provisioning/dashboards/dashboards.yml
      - ./grafana/dashboards:/var/lib/grafana/dashboards
    depends_on:
      - prometheus
      - jaeger
```

---

## Risks and Mitigations

### Risk 1: Performance Overhead
**Impact**: OpenTelemetry instrumentation may add latency to requests

**Mitigation**:
- Use sampling (e.g., 10% of requests traced in production)
- Async exporters to avoid blocking request handling
- Benchmark before/after instrumentation

### Risk 2: Data Volume
**Impact**: High-traffic RAG queries generate large trace/metric volumes

**Mitigation**:
- Configure Jaeger retention policies
- Use Prometheus recording rules for downsampling
- Implement trace sampling strategies

### Risk 3: Configuration Complexity
**Impact**: Multiple services and configuration files to maintain

**Mitigation**:
- Provide sensible defaults in `backend/config.py`
- Document all configuration options
- Use environment variables for deployment flexibility

---

## Decision Points

### ✅ Confirmed Decisions

1. **Use OpenTelemetry SDK** for instrumentation (industry standard, vendor-neutral)
2. **Jaeger for traces** (lightweight, good Docker support, OTLP compatible)
3. **Prometheus for metrics** (standard for time-series, Grafana integration)
4. **Grafana for dashboards** (unified UI for metrics + traces)
5. **Keep existing `OpenAIUsageMonitor`** for backward compatibility, extend with OTel metrics

### 🔄 Pending Decisions

1. **Sampling rate for production** (recommend 10%, configurable via env var)
2. **Jaeger storage backend** (in-memory for dev, what for prod?)
3. **Metric naming convention** (follow OpenTelemetry semantic conventions)

---

## Next Steps

1. Create SPEC-DELTA.md with acceptance criteria
2. Create PLAN.md with implementation steps
3. Verify OpenTelemetry package versions via Context7
4. Implement instrumentation following TDD approach
