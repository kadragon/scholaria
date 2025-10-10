# SPEC: OpenTelemetry Observability Integration

**Version**: 1.0.0
**Status**: Draft
**Date**: 2025-10-10

---

## Overview

Add comprehensive observability to the Scholaria RAG system using OpenTelemetry for distributed tracing, metrics collection, and performance monitoring.

---

## Acceptance Criteria

### AC1: OpenTelemetry Instrumentation
**Given** the FastAPI application is running
**When** a RAG query is processed
**Then** the request generates traces with the following spans:
- `http.request` (auto-instrumented by FastAPI)
- `rag.query` (custom span wrapping entire pipeline)
- `rag.embedding` (embedding generation)
- `rag.vector_search` (Qdrant search)
- `rag.rerank` (BGE reranking)
- `rag.llm_generation` (OpenAI chat completion)

**And** each span includes relevant attributes:
- `query.length`, `topic_ids.count` on `rag.query`
- `cache.hit` (boolean) on `rag.embedding`
- `results.count` on `rag.vector_search`, `rag.rerank`
- `model.name`, `tokens.prompt`, `tokens.completion` on `rag.llm_generation`

### AC2: Jaeger Integration
**Given** Jaeger is running in Docker Compose
**When** traces are collected
**Then** traces are visible in Jaeger UI at `http://localhost:16686`
**And** spans show parent-child relationships correctly
**And** span duration and timing information is accurate

### AC3: Prometheus Metrics
**Given** Prometheus is running and scraping the backend
**When** metrics endpoint `/metrics` is queried
**Then** the following metrics are exposed:
- `rag_query_duration_seconds` (histogram) - end-to-end query latency
- `rag_embedding_cache_hits_total` (counter) - embedding cache hits
- `rag_embedding_cache_misses_total` (counter) - embedding cache misses
- `rag_vector_search_results_count` (histogram) - result count distribution
- `rag_openai_tokens_total` (counter, labels: `type=[prompt|completion]`) - token usage
- `rag_query_errors_total` (counter, labels: `stage=[embedding|search|rerank|llm]`) - errors by stage

### AC4: Grafana Dashboard
**Given** Grafana is running with Prometheus and Jaeger data sources
**When** the RAG dashboard is loaded
**Then** the dashboard displays:
- Request rate and latency (p50, p95, p99)
- Error rate by stage
- Cache hit ratio charts
- Token usage over time
- Top 10 slowest queries (via Jaeger links)

### AC5: Configuration
**Given** `backend/config.py` settings
**When** observability is configured via environment variables
**Then** the following settings are available:
- `OTEL_ENABLED` (bool, default: `True`)
- `OTEL_SERVICE_NAME` (str, default: `"scholaria-backend"`)
- `OTEL_EXPORTER_OTLP_ENDPOINT` (str, default: `"http://jaeger:4317"`)
- `OTEL_TRACES_SAMPLER` (str, default: `"parentbased_traceidratio"`)
- `OTEL_TRACES_SAMPLER_ARG` (float, default: `1.0` for dev, `0.1` for prod)
- `PROMETHEUS_METRICS_PORT` (int, default: `8000` - use FastAPI app port)

### AC6: Backward Compatibility
**Given** existing `OpenAIUsageMonitor` is in use
**When** OpenTelemetry is enabled
**Then** `OpenAIUsageMonitor` continues to function
**And** its metrics are also exported via OpenTelemetry metrics API
**And** existing tests for `OpenAIUsageMonitor` still pass

### AC7: Testing
**Given** test suite for observability
**When** tests are run
**Then** the following are validated:
- Trace spans are created for each RAG pipeline stage
- Span attributes contain expected values
- Metrics are incremented correctly
- Instrumentation does not break existing functionality
- Performance overhead is < 5% for traced requests

### AC8: Documentation
**Given** deployment and user documentation
**When** observability feature is released
**Then** documentation includes:
- Setup instructions for Jaeger, Prometheus, Grafana
- Configuration reference for all OTEL settings
- Dashboard usage guide with screenshots
- Troubleshooting section for common issues
- Performance impact notes and sampling recommendations

---

## Interface

### New Module: `backend/observability.py`

```python
from opentelemetry import trace, metrics
from fastapi import FastAPI

def setup_observability(app: FastAPI) -> None:
    """Configure OpenTelemetry instrumentation for the application."""
    ...

def get_tracer(name: str) -> trace.Tracer:
    """Get a tracer instance for manual instrumentation."""
    ...

def get_meter(name: str) -> metrics.Meter:
    """Get a meter instance for custom metrics."""
    ...
```

### Updated Module: `backend/services/rag_service.py`

```python
from backend.observability import get_tracer, get_meter

class AsyncRAGService:
    def __init__(self, ...):
        self.tracer = get_tracer(__name__)
        self.meter = get_meter(__name__)
        self._setup_metrics()

    def _setup_metrics(self):
        self.query_duration = self.meter.create_histogram("rag.query.duration")
        self.cache_hits = self.meter.create_counter("rag.embedding.cache.hits")
        ...

    async def query(self, query: str, topic_ids: list[int], ...):
        with self.tracer.start_as_current_span("rag.query") as span:
            span.set_attribute("query.length", len(query))
            ...
```

---

## Examples

### Example 1: Trace in Jaeger UI

```
Trace ID: 1a2b3c4d5e6f7g8h
Duration: 1.2s

├─ http.request (1.2s)
│  └─ rag.query (1.15s)
│     ├─ rag.embedding (0.05s) [cache.hit=false]
│     ├─ rag.vector_search (0.3s) [results.count=10]
│     ├─ rag.rerank (0.2s) [results.count=5]
│     └─ rag.llm_generation (0.6s) [model.name=gpt-4o-mini, tokens.prompt=1500, tokens.completion=250]
```

### Example 2: Prometheus Query

```promql
# Average query latency (95th percentile)
histogram_quantile(0.95, rate(rag_query_duration_seconds_bucket[5m]))

# Cache hit ratio
rate(rag_embedding_cache_hits_total[5m]) /
  (rate(rag_embedding_cache_hits_total[5m]) + rate(rag_embedding_cache_misses_total[5m]))

# Error rate by stage
sum(rate(rag_query_errors_total[5m])) by (stage)
```

### Example 3: Grafana Dashboard Panel (JSON)

```json
{
  "title": "RAG Query Latency",
  "targets": [
    {
      "expr": "histogram_quantile(0.95, rate(rag_query_duration_seconds_bucket[5m]))",
      "legendFormat": "p95"
    },
    {
      "expr": "histogram_quantile(0.50, rate(rag_query_duration_seconds_bucket[5m]))",
      "legendFormat": "p50"
    }
  ],
  "type": "graph"
}
```

---

## Dependencies

| Name | Latest | Release | Chosen | Rationale | Link |
|------|--------|---------|--------|-----------|------|
| opentelemetry-api | 1.37.0 | 2025-09-11 | 1.37.0 | Core OTel API (stable) | [PyPI](https://pypi.org/project/opentelemetry-api/) |
| opentelemetry-sdk | 1.37.0 | 2025-09-11 | 1.37.0 | SDK implementation (stable) | [PyPI](https://pypi.org/project/opentelemetry-sdk/) |
| opentelemetry-instrumentation-fastapi | 0.58b0 | 2025-09-11 | 0.58b0 | FastAPI auto-instrumentation (beta, prod-ready) | [PyPI](https://pypi.org/project/opentelemetry-instrumentation-fastapi/) |
| opentelemetry-instrumentation-httpx | 0.58b0 | 2025-09-11 | 0.58b0 | OpenAI client instrumentation (beta, prod-ready) | [PyPI](https://pypi.org/project/opentelemetry-instrumentation-httpx/) |
| opentelemetry-instrumentation-redis | 0.58b0 | 2025-09-11 | 0.58b0 | Redis cache instrumentation (beta, prod-ready) | [PyPI](https://pypi.org/project/opentelemetry-instrumentation-redis/) |
| opentelemetry-exporter-otlp-proto-grpc | 1.37.0 | 2025-09-11 | 1.37.0 | Jaeger OTLP exporter (stable) | [PyPI](https://pypi.org/project/opentelemetry-exporter-otlp-proto-grpc/) |
| opentelemetry-exporter-prometheus | 0.58b0 | 2025-09-11 | 0.58b0 | Prometheus metrics exporter (beta, prod-ready) | [PyPI](https://pypi.org/project/opentelemetry-exporter-prometheus/) |

**Docker Images**:
- `jaegertracing/all-in-one:latest` (or specific version after verification)
- `prom/prometheus:latest` (or specific version)
- `grafana/grafana:latest` (or specific version)

---

## Migration Impact

### Breaking Changes
**None** - This is an additive feature.

### Deprecations
**None** - Existing `OpenAIUsageMonitor` remains supported.

### Configuration Changes
**New environment variables** (all optional with defaults):
- `OTEL_ENABLED`
- `OTEL_SERVICE_NAME`
- `OTEL_EXPORTER_OTLP_ENDPOINT`
- `OTEL_TRACES_SAMPLER`
- `OTEL_TRACES_SAMPLER_ARG`

### Database Changes
**None**

### API Changes
**New endpoint**:
- `GET /metrics` - Prometheus scrape endpoint (exposed on main app port)

---

## Rollback Strategy

1. Set `OTEL_ENABLED=false` in environment variables
2. Remove Jaeger, Prometheus, Grafana services from `docker-compose.yml`
3. Restart backend service

**Verification**:
- Application logs show "OpenTelemetry disabled"
- No traces appear in Jaeger
- `/metrics` endpoint returns 404 or minimal metrics

---

## Performance Considerations

### Overhead Estimation
- **Trace span creation**: ~0.1-0.5ms per span
- **Metric recording**: ~0.01-0.05ms per metric
- **Exporter batching**: async, non-blocking
- **Expected total overhead**: < 5% for p95 latency

### Sampling Strategy
- **Development**: 100% sampling for debugging
- **Production**: 10% sampling (configurable)
- **Adaptive sampling**: Consider implementing based on error rates (future enhancement)

### Resource Usage
- **Jaeger (in-memory)**: ~200MB RAM
- **Prometheus**: ~100MB RAM + disk for TSDB
- **Grafana**: ~150MB RAM
- **Total additional**: ~450MB RAM (acceptable for observability value)

---

## Security Considerations

1. **Sensitive Data in Traces**:
   - DO NOT include user query content in span attributes (only length)
   - DO NOT include API keys or tokens in spans
   - Sanitize error messages before adding to spans

2. **Access Control**:
   - Jaeger UI should be behind authentication in production
   - Prometheus metrics endpoint should not expose sensitive business data
   - Grafana requires admin password (default `admin`, should be changed)

3. **Network Exposure**:
   - Development: expose Jaeger/Grafana ports for local access
   - Production: use internal network only, access via VPN or proxy

---

## Alternatives Considered

### Alternative 1: Custom Logging + ELK Stack
**Pros**: Full control, rich log analysis
**Rejected**: Higher operational complexity, no native distributed tracing

### Alternative 2: DataDog / New Relic APM
**Pros**: Managed service, comprehensive features
**Rejected**: Cost prohibitive, vendor lock-in

### Alternative 3: Continue with `OpenAIUsageMonitor` only
**Pros**: No additional dependencies
**Rejected**: Lacks distributed tracing, no request correlation, limited visualization

---

## Open Questions

1. ❓ **Jaeger storage**: In-memory for dev, what for production? (Cassandra, Elasticsearch, or managed service?)
2. ❓ **Metric retention**: How long should Prometheus retain metrics? (Recommend 15 days for dev, 90 days for prod)
3. ❓ **Dashboard customization**: Should we provide multiple dashboards (overview, detailed, error analysis)?

---

## Changelog

- **2025-10-10**: Initial draft with core acceptance criteria and interface design
