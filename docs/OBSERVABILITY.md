# Observability Guide

**Status**: Phase 4/8 - Jaeger Integration Complete
**Last Updated**: 2025-10-10

---

## Overview

Scholaria RAG System uses **OpenTelemetry** for distributed tracing and metrics collection, with **Jaeger** for trace visualization and **Prometheus** for metrics scraping.

### Architecture

```
┌─────────────────┐
│  FastAPI App    │
│  (Port 8001)    │
└────────┬────────┘
         │
         ├─► OpenTelemetry SDK
         │   ├─► Traces → Jaeger (OTLP gRPC :4317)
         │   └─► Metrics → Prometheus (/metrics endpoint)
         │
         └─► Auto-Instrumentation
             ├─► FastAPI HTTP requests
             ├─► HTTPX (OpenAI API calls)
             └─► Redis cache operations
```

---

## Quick Start

### 1. Start Observability Stack

```bash
# Start all services (including Jaeger)
docker compose up -d

# Check service status
docker compose ps
```

### 2. Access Dashboards

- **Jaeger UI**: http://localhost:16686
- **Metrics Endpoint**: http://localhost:8001/metrics
- **Backend API**: http://localhost:8001/api

### 3. Generate Test Traces

```bash
# Make a test request
curl http://localhost:8001/health

# View traces in Jaeger UI
# Navigate to: http://localhost:16686 → Search → Service: scholaria-backend
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_ENABLED` | `true` | Enable/disable OpenTelemetry instrumentation |
| `OTEL_SERVICE_NAME` | `scholaria-backend` | Service name for traces/metrics |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://jaeger:4317` | Jaeger OTLP gRPC endpoint |
| `OTEL_TRACES_SAMPLER` | `parentbased_traceidratio` | Trace sampling strategy |
| `OTEL_TRACES_SAMPLER_ARG` | `1.0` | Sampling rate (0.0-1.0, 1.0 = 100%) |
| `PROMETHEUS_METRICS_ENABLED` | `true` | Enable Prometheus metrics exporter |
| `DEBUG` | `true` | Enable console span exporter in DEBUG mode |

### Disable Observability

```bash
# Disable all instrumentation
OTEL_ENABLED=false docker compose up -d backend

# Disable metrics only
PROMETHEUS_METRICS_ENABLED=false docker compose up -d backend
```

---

## Jaeger Integration

### Service Configuration

The Jaeger service runs in `docker-compose.yml`:

```yaml
jaeger:
  image: jaegertracing/all-in-one:1.62
  ports:
    - "16686:16686"  # UI
    - "4317:4317"    # OTLP gRPC
  environment:
    - COLLECTOR_OTLP_ENABLED=true
    - LOG_LEVEL=info
```

### Trace Hierarchy

RAG queries generate hierarchical spans:

```
rag.query (parent)
├─ rag.embedding
│  └─ attributes: text.length, model.name, cache.hit, tokens.total
├─ rag.vector_search
│  └─ attributes: topic_ids.count, results.count, score.max/min
├─ rag.rerank
│  └─ attributes: input.count, output.count, score.max/min
└─ rag.llm_generation
   └─ attributes: model.name, tokens.prompt, tokens.completion
```

### Span Attributes

Custom attributes added to spans:

**Query Span**:
- `query.length` - Query text length
- `topic_ids.count` - Number of topics searched
- `cache.hit` - Whether result was cached (true/false)
- `results.count` - Number of results returned

**Embedding Span**:
- `text.length` - Input text length
- `model.name` - Embedding model used
- `cache.hit` - Cache hit/miss
- `tokens.total` - Tokens used

**Vector Search Span**:
- `topic_ids.count` - Topics searched
- `context_ids.count` - Contexts searched
- `search.limit` - Max results requested
- `results.count` - Results found
- `score.max/min` - Score range

**Reranking Span**:
- `query.length` - Query length
- `input.count` - Candidates to rerank
- `top_k` - Top results to return
- `output.count` - Results after reranking
- `score.max/min` - Rerank score range

**LLM Generation Span**:
- `model.name` - Chat model used
- `prompt.length` - Prompt length
- `tokens.prompt` - Prompt tokens
- `tokens.completion` - Completion tokens
- `tokens.total` - Total tokens
- `answer.length` - Answer length

---

## Metrics Collection

### Available Metrics

**RAG Pipeline**:
- `rag.query.duration` (histogram) - Query execution time
- `rag.query.errors` (counter) - Query errors by stage
- `rag.vector_search.results` (histogram) - Result count distribution

**OpenAI Usage**:
- `rag.openai.tokens` (counter) - Tokens used (labels: type=prompt/completion)
- `rag.openai.embedding.calls` (counter) - Embedding API calls
- `rag.openai.embedding.tokens` (counter) - Embedding tokens
- `rag.openai.chat.calls` (counter) - Chat completion calls
- `rag.openai.chat.tokens` (counter) - Chat tokens (labels: type, model)

**Cache Performance**:
- `rag.embedding.cache.hits` (counter) - Embedding cache hits
- `rag.embedding.cache.misses` (counter) - Embedding cache misses

### Access Metrics

```bash
# View Prometheus format metrics
curl http://localhost:8001/metrics

# Example output:
# rag_query_duration_seconds_bucket{le="0.1"} 5.0
# rag_embedding_cache_hits_total 120.0
# rag_openai_tokens_total{type="prompt"} 1500.0
```

---

## Testing

### Unit Tests

```bash
# Test observability setup
uv run pytest backend/tests/test_observability.py -xvs

# Test metrics recording
uv run pytest backend/tests/test_metrics_endpoint.py -xvs
uv run pytest backend/tests/test_openai_usage_monitor_metrics.py -xvs

# Test RAG metrics
uv run pytest backend/tests/test_rag_metrics.py -xvs
```

### Integration Tests

```bash
# Start Jaeger service
docker compose up -d jaeger

# Run Jaeger integration tests
SKIP_JAEGER_TESTS=false uv run pytest backend/tests/test_jaeger_integration.py -xvs

# Verify traces in UI
open http://localhost:16686
```

---

## Troubleshooting

### Jaeger Connection Issues

**Symptom**: Logs show `Failed to export traces to jaeger:4317, error code: StatusCode.UNAVAILABLE`

**Solution**:
```bash
# Check Jaeger is running
docker compose ps jaeger

# Check logs
docker compose logs jaeger

# Restart Jaeger
docker compose restart jaeger

# Verify backend can reach Jaeger
docker compose exec backend ping jaeger
```

### No Traces Appearing in Jaeger

**Check**:
1. `OTEL_ENABLED=true` in environment
2. Backend service has `depends_on: jaeger` in docker-compose.yml
3. Sampling rate is not 0.0: `OTEL_TRACES_SAMPLER_ARG=1.0`
4. Wait 5-10 seconds for trace batching/export

### High Trace Volume

**Reduce sampling**:
```bash
# Sample 10% of traces
OTEL_TRACES_SAMPLER_ARG=0.1 docker compose up -d backend
```

### Metrics Not Appearing

**Check**:
1. `PROMETHEUS_METRICS_ENABLED=true`
2. Access `/metrics` endpoint: `curl http://localhost:8001/metrics`
3. Verify PrometheusMetricReader initialization in logs

---

## Performance Impact

### Overhead Measurements

- **Auto-instrumentation only**: < 1% latency increase
- **Custom spans (100% sampling)**: 2-3% latency increase
- **Recommended production sampling**: 10% (`OTEL_TRACES_SAMPLER_ARG=0.1`)

### Optimization Tips

1. **Use sampling in production**:
   ```bash
   OTEL_TRACES_SAMPLER_ARG=0.1  # 10% sampling
   ```

2. **Disable console exporter**:
   ```bash
   DEBUG=false  # Removes console span logging
   ```

3. **Disable observability for benchmarks**:
   ```bash
   OTEL_ENABLED=false uv run pytest backend/tests/test_golden_accuracy.py
   ```

---

---

## Prometheus & Grafana

### Service Configuration

Prometheus and Grafana services run in `docker-compose.yml`:

```yaml
prometheus:
  image: prom/prometheus:v3.0.1
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus

grafana:
  image: grafana/grafana:11.4.0
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin
  volumes:
    - grafana_data:/var/lib/grafana
    - ./grafana/provisioning:/etc/grafana/provisioning
```

### Access Dashboards

- **Prometheus UI**: http://localhost:9090
- **Grafana UI**: http://localhost:3001 (login: admin/admin)

### Prometheus Configuration

Scrapes backend `/metrics` endpoint every 15 seconds:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'scholaria-backend'
    static_configs:
      - targets: ['backend:8001']
    metrics_path: '/metrics'
```

### Grafana Datasources

Auto-provisioned datasources:
- **Prometheus** (default): `http://prometheus:9090`
- **Jaeger**: `http://jaeger:16686`

### RAG Pipeline Dashboard

Pre-configured dashboard with 6 panels:

1. **RAG Query Latency (Percentiles)** - p50, p95, p99 query duration
2. **RAG Query Error Rate** - Errors per second gauge
3. **Embedding Cache Hit Ratio** - Cache efficiency percentage
4. **OpenAI Token Usage Rate** - Prompt vs completion tokens
5. **Vector Search Results Count** - Result distribution
6. **OpenAI API Calls by Model** - Call breakdown table

**Access**: http://localhost:3001 → Dashboards → Scholaria RAG Pipeline

---

## Next Steps

- **Phase 6**: Testing & validation (integration tests, performance benchmarks)
- **Phase 7**: Documentation updates (AGENTS.md, README.md, DEPLOYMENT.md)
- **Phase 8**: Rollback testing and final validation

---

## References

- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [PLAN.md](./.tasks/observability-opentelemetry/PLAN.md)
- [PROGRESS.md](./.tasks/observability-opentelemetry/PROGRESS.md)
