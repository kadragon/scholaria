# Implementation Plan: OpenTelemetry Observability

**Task ID**: observability-opentelemetry
**Date**: 2025-10-10
**Status**: Planning Complete

---

## Goals

1. **Instrument RAG pipeline** with OpenTelemetry distributed tracing
2. **Export traces** to Jaeger for visualization
3. **Expose metrics** via Prometheus exporter
4. **Provide Grafana dashboard** for RAG performance monitoring
5. **Maintain backward compatibility** with existing `OpenAIUsageMonitor`
6. **Achieve < 5% performance overhead** with proper sampling

---

## Dependencies

### Python Packages (Verified 2025-10-10)

| Package | Version | Released | Rationale | Link |
|---------|---------|----------|-----------|------|
| opentelemetry-api | 1.37.0 | 2025-09-11 | Core OTel API (stable) | [PyPI](https://pypi.org/project/opentelemetry-api/) |
| opentelemetry-sdk | 1.37.0 | 2025-09-11 | SDK implementation (stable) | [PyPI](https://pypi.org/project/opentelemetry-sdk/) |
| opentelemetry-instrumentation-fastapi | 0.58b0 | 2025-09-11 | FastAPI auto-instrumentation (beta, stable enough) | [PyPI](https://pypi.org/project/opentelemetry-instrumentation-fastapi/) |
| opentelemetry-instrumentation-httpx | 0.58b0 | 2025-09-11 | HTTPX instrumentation for OpenAI client | [PyPI](https://pypi.org/project/opentelemetry-instrumentation-httpx/) |
| opentelemetry-instrumentation-redis | 0.58b0 | 2025-09-11 | Redis cache instrumentation | [PyPI](https://pypi.org/project/opentelemetry-instrumentation-redis/) |
| opentelemetry-exporter-otlp-proto-grpc | 1.37.0 | 2025-09-11 | Jaeger OTLP gRPC exporter | [PyPI](https://pypi.org/project/opentelemetry-exporter-otlp-proto-grpc/) |
| opentelemetry-exporter-prometheus | 0.58b0 | 2025-09-11 | Prometheus metrics exporter | [PyPI](https://pypi.org/project/opentelemetry-exporter-prometheus/) |

**Note**: All packages use latest stable/beta versions as of 2025-09-11. Beta instrumentation packages (0.58b0) are production-ready per OpenTelemetry Python project standards.

### Docker Images

- **Jaeger**: `jaegertracing/all-in-one:1.62` (latest stable as of 2025-10)
- **Prometheus**: `prom/prometheus:v3.0.1` (latest stable)
- **Grafana**: `grafana/grafana:11.4.0` (latest stable)

---

## Implementation Steps

### Phase 1: Foundation (TDD Setup)

**Target**: Set up OpenTelemetry SDK with console exporter for local testing

#### Step 1.1: Add Dependencies
- [ ] Update `pyproject.toml` with OpenTelemetry packages
- [ ] Run `uv sync` to install dependencies
- [ ] Verify imports in a test script

**Files**:
- `pyproject.toml` (add dependencies under `[project.dependencies]`)

**Test**: `uv sync` succeeds, no import errors

---

#### Step 1.2: Create Observability Module
- [ ] Create `backend/observability.py` with configuration functions
- [ ] Implement `setup_observability(app: FastAPI)` with console exporter
- [ ] Implement `get_tracer(name: str)` and `get_meter(name: str)` helpers

**Files**:
- `backend/observability.py` (new)

**Acceptance**:
- Module imports successfully
- `setup_observability` initializes TracerProvider and MeterProvider
- Console exporter logs traces to stdout

**Test Strategy**:
```python
# backend/tests/test_observability.py
def test_setup_observability_initializes_providers():
    from backend.observability import setup_observability
    from fastapi import FastAPI
    app = FastAPI()
    setup_observability(app)
    # Assert TracerProvider is set
    from opentelemetry import trace
    assert trace.get_tracer_provider() is not None
```

---

#### Step 1.3: Integrate with FastAPI App
- [ ] Call `setup_observability(app)` in `backend/main.py`
- [ ] Add feature flag `OTEL_ENABLED` to `backend/config.py`
- [ ] Verify auto-instrumentation generates spans for HTTP requests

**Files**:
- `backend/main.py` (add observability setup)
- `backend/config.py` (add OTEL settings)

**Acceptance**:
- HTTP requests generate `http.request` spans visible in console
- Setting `OTEL_ENABLED=false` disables instrumentation

**Test Strategy**:
```python
# backend/tests/test_main.py
def test_app_with_observability_enabled(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    # Check console output for span logs (integration test)
```

---

### Phase 2: Custom RAG Pipeline Spans

**Target**: Add custom spans for RAG components (embedding, search, rerank, LLM)

#### Step 2.1: Instrument EmbeddingService
- [ ] Add `tracer = get_tracer(__name__)` in `backend/retrieval/embeddings.py`
- [ ] Wrap `generate_embedding` with span: `rag.embedding`
- [ ] Add span attributes: `cache.hit`, `text.length`, `model.name`

**Files**:
- `backend/retrieval/embeddings.py`

**Acceptance**:
- Embedding calls generate `rag.embedding` spans
- Cache hits/misses are visible in span attributes

**Test Strategy**:
```python
# backend/tests/test_embeddings_tracing.py
def test_embedding_creates_span(mocker):
    from backend.retrieval.embeddings import EmbeddingService
    service = EmbeddingService()

    # Mock OpenAI client
    mocker.patch.object(service.client.embeddings, 'create', ...)

    # Generate embedding
    service.generate_embedding("test query")

    # Assert span was created with correct attributes
    # (use in-memory span exporter to capture spans)
```

---

#### Step 2.2: Instrument AsyncRAGService
- [ ] Add tracer and meter in `AsyncRAGService.__init__`
- [ ] Wrap `query()` method with `rag.query` span
- [ ] Add child spans for vector search, reranking, LLM generation
- [ ] Add span attributes: `query.length`, `topic_ids.count`, `results.count`, `tokens.prompt`, `tokens.completion`

**Files**:
- `backend/services/rag_service.py`

**Acceptance**:
- RAG queries generate hierarchical spans:
  ```
  rag.query
  ├─ rag.embedding
  ├─ rag.vector_search
  ├─ rag.rerank
  └─ rag.llm_generation
  ```

**Test Strategy**:
```python
# backend/tests/test_rag_service_tracing.py
async def test_rag_query_creates_spans(mocker, async_rag_service):
    # Mock all dependencies
    mocker.patch.object(async_rag_service.embedding_service, 'generate_embedding', ...)
    mocker.patch.object(async_rag_service.qdrant_service, 'search_similar', ...)

    # Execute query
    result = await async_rag_service.query("test", topic_ids=[1])

    # Assert spans exist and have correct hierarchy
    # (use in-memory span exporter)
```

---

#### Step 2.3: Instrument Reranking and Qdrant Services
- [ ] Add spans to `RerankingService.rerank_results`
- [ ] Add spans to `QdrantService.search_similar`
- [ ] Add relevant attributes (result counts, scores)

**Files**:
- `backend/retrieval/reranking.py`
- `backend/retrieval/qdrant.py`

**Acceptance**:
- Reranking and vector search operations are traced
- Span attributes show result counts and scores

---

### Phase 3: Metrics Collection

**Target**: Expose Prometheus metrics for RAG pipeline

#### Step 3.1: Define Custom Metrics
- [ ] Create histogram: `rag_query_duration_seconds`
- [ ] Create counters: `rag_embedding_cache_hits_total`, `rag_embedding_cache_misses_total`
- [ ] Create histogram: `rag_vector_search_results_count`
- [ ] Create counter: `rag_openai_tokens_total` (labels: `type=[prompt|completion]`)
- [ ] Create counter: `rag_query_errors_total` (labels: `stage`)

**Files**:
- `backend/services/rag_service.py` (add metric recording in pipeline)
- `backend/retrieval/embeddings.py` (add cache metrics)

**Acceptance**:
- Metrics are recorded during RAG operations
- Metrics endpoint `/metrics` exposes Prometheus format

**Test Strategy**:
```python
# backend/tests/test_rag_metrics.py
async def test_rag_query_records_metrics(client, async_rag_service):
    # Execute query
    result = await async_rag_service.query("test", topic_ids=[1])

    # Fetch /metrics endpoint
    response = client.get("/metrics")
    assert "rag_query_duration_seconds" in response.text
    assert "rag_embedding_cache_hits_total" in response.text
```

---

#### Step 3.2: Integrate OpenAIUsageMonitor with Metrics
- [ ] Export `OpenAIUsageMonitor` metrics as OpenTelemetry metrics
- [ ] Ensure backward compatibility with existing methods

**Files**:
- `backend/retrieval/monitoring.py`

**Acceptance**:
- Existing `OpenAIUsageMonitor` methods continue to work
- Usage metrics are also exposed via `/metrics`

---

### Phase 4: Jaeger Integration

**Target**: Export traces to Jaeger via OTLP

#### Step 4.1: Add OTLP Exporter
- [ ] Replace console exporter with `OTLPSpanExporter` in `backend/observability.py`
- [ ] Add configuration: `OTEL_EXPORTER_OTLP_ENDPOINT` (default: `http://jaeger:4317`)
- [ ] Add sampling configuration: `OTEL_TRACES_SAMPLER_ARG` (default: 1.0)

**Files**:
- `backend/observability.py`
- `backend/config.py`

**Acceptance**:
- Traces are exported to Jaeger OTLP endpoint
- Sampling configuration is respected

---

#### Step 4.2: Add Jaeger Service to Docker Compose
- [ ] Add `jaeger` service to `docker-compose.yml`
- [ ] Expose ports: 16686 (UI), 4317 (OTLP gRPC)
- [ ] Configure environment: `COLLECTOR_OTLP_ENABLED=true`

**Files**:
- `docker-compose.yml`

**Acceptance**:
- `docker compose up jaeger` starts Jaeger successfully
- Jaeger UI accessible at `http://localhost:16686`
- Backend can connect to `jaeger:4317`

**Test Strategy**:
```bash
# Integration test
docker compose up -d jaeger backend
curl http://localhost:8000/api/health
# Check Jaeger UI for traces at http://localhost:16686
```

---

### Phase 5: Prometheus & Grafana Integration

**Target**: Set up Prometheus scraping and Grafana dashboards

#### Step 5.1: Configure Prometheus
- [ ] Create `prometheus.yml` with scrape config for backend `/metrics`
- [ ] Add `prometheus` service to `docker-compose.yml`
- [ ] Expose port 9090

**Files**:
- `prometheus.yml` (new)
- `docker-compose.yml`

**Acceptance**:
- Prometheus scrapes backend metrics every 15 seconds
- Prometheus UI at `http://localhost:9090` shows targets

---

#### Step 5.2: Set Up Grafana
- [ ] Add `grafana` service to `docker-compose.yml`
- [ ] Create `grafana/datasources.yml` (Prometheus + Jaeger)
- [ ] Create `grafana/dashboards.yml` (dashboard provisioning)
- [ ] Expose port 3001

**Files**:
- `docker-compose.yml`
- `grafana/datasources.yml` (new)
- `grafana/dashboards.yml` (new)

**Acceptance**:
- Grafana UI at `http://localhost:3001`
- Prometheus and Jaeger data sources configured
- Login: `admin/admin`

---

#### Step 5.3: Create RAG Dashboard
- [ ] Create `grafana/dashboards/rag-pipeline.json`
- [ ] Add panels: query latency (p50, p95, p99), error rate, cache hit ratio, token usage
- [ ] Add links to Jaeger traces for slow queries

**Files**:
- `grafana/dashboards/rag-pipeline.json` (new)

**Acceptance**:
- Dashboard shows real-time RAG metrics
- Clicking on slow queries opens Jaeger trace view

---

### Phase 6: Testing & Validation

**Target**: Comprehensive test coverage and performance validation

#### Step 6.1: Unit Tests
- [ ] Test `backend/observability.py` initialization
- [ ] Test span creation in EmbeddingService, AsyncRAGService, RerankingService
- [ ] Test metric recording

**Files**:
- `backend/tests/test_observability.py`
- `backend/tests/test_embeddings_tracing.py`
- `backend/tests/test_rag_service_tracing.py`
- `backend/tests/test_rag_metrics.py`

**Coverage Target**: ≥ 80% for new observability code

---

#### Step 6.2: Integration Tests
- [ ] Test end-to-end trace export to Jaeger
- [ ] Test Prometheus scraping from `/metrics`
- [ ] Test Grafana dashboard rendering

**Files**:
- `backend/tests/integration/test_observability_integration.py` (new)

**Test Strategy**:
```python
# Integration test (requires Docker)
def test_traces_appear_in_jaeger():
    # Start services: docker compose up -d
    # Make request to backend
    # Query Jaeger API for traces
    # Assert trace exists
```

---

#### Step 6.3: Performance Benchmarking
- [ ] Measure p95 latency with observability disabled
- [ ] Measure p95 latency with observability enabled (100% sampling)
- [ ] Measure p95 latency with observability enabled (10% sampling)
- [ ] Verify overhead < 5%

**Test Strategy**:
```bash
# Use existing golden dataset benchmark
uv run pytest backend/tests/test_golden_accuracy.py --benchmark
# Compare results with/without OTEL_ENABLED
```

---

### Phase 7: Documentation

**Target**: Comprehensive documentation for deployment and usage

#### Step 7.1: Update Core Documentation
- [ ] Update `.agents/AGENTS.md` with observability workflow
- [ ] Update `backend/README.md` with setup instructions
- [ ] Update `docs/DEPLOYMENT.md` with Jaeger/Prometheus/Grafana setup

**Files**:
- `.agents/AGENTS.md`
- `backend/README.md`
- `docs/DEPLOYMENT.md`

---

#### Step 7.2: Create Observability Guide
- [ ] Create `docs/OBSERVABILITY.md` with:
  - Architecture overview
  - Configuration reference
  - Dashboard usage guide
  - Troubleshooting section
  - Performance tuning recommendations

**Files**:
- `docs/OBSERVABILITY.md` (new)

---

### Phase 8: Rollback & Cleanup

**Target**: Ensure safe rollback path and finalize implementation

#### Step 8.1: Test Rollback Procedure
- [ ] Set `OTEL_ENABLED=false` and verify no instrumentation
- [ ] Remove Jaeger/Prometheus/Grafana from `docker-compose.yml` and verify app still works

**Test Strategy**:
```bash
OTEL_ENABLED=false docker compose up -d backend
# Verify app health
curl http://localhost:8000/api/health
# Verify no traces in logs
```

---

#### Step 8.2: Final Validation
- [ ] Run full test suite: `uv run pytest`
- [ ] Run linters: `uv run ruff check .`, `uv run ruff format --check .`
- [ ] Run type checker: `uv run mypy .`
- [ ] Verify 201 tests pass, 85% backend coverage maintained

---

## Test Strategy Summary

### Unit Tests (TDD)
- **Scope**: Individual modules (observability.py, embeddings.py, rag_service.py)
- **Approach**: Red → Green → Refactor
- **Tools**: pytest, pytest-asyncio, pytest-mock
- **Coverage Target**: ≥ 80% for new code

### Integration Tests
- **Scope**: End-to-end trace/metric export
- **Approach**: Docker Compose-based
- **Tools**: pytest, Docker SDK, Jaeger/Prometheus APIs
- **Coverage**: Critical paths (RAG query → Jaeger trace, /metrics → Prometheus)

### Performance Tests
- **Scope**: Latency overhead measurement
- **Approach**: Benchmark with/without observability
- **Tools**: pytest-benchmark, golden dataset
- **Target**: < 5% overhead at p95

---

## Rollback Plan

1. **Disable OpenTelemetry**: Set `OTEL_ENABLED=false` in `.env`
2. **Restart Backend**: `docker compose restart backend`
3. **Remove Observability Stack** (optional): Comment out `jaeger`, `prometheus`, `grafana` in `docker-compose.yml`

**Verification**:
- No spans logged to console
- Application continues to function normally
- Existing `OpenAIUsageMonitor` metrics still available via API

---

## Success Criteria

- ✅ All 201 existing tests pass
- ✅ New observability tests pass (≥ 80% coverage)
- ✅ Jaeger UI shows RAG traces with correct hierarchy
- ✅ Prometheus scrapes metrics successfully
- ✅ Grafana dashboard displays real-time RAG metrics
- ✅ Performance overhead < 5% at p95
- ✅ Documentation complete (OBSERVABILITY.md, deployment guide)
- ✅ Rollback procedure validated

---

## Timeline Estimate

- **Phase 1 (Foundation)**: 2-3 hours
- **Phase 2 (RAG Spans)**: 3-4 hours
- **Phase 3 (Metrics)**: 2-3 hours
- **Phase 4 (Jaeger)**: 1-2 hours
- **Phase 5 (Prometheus/Grafana)**: 2-3 hours
- **Phase 6 (Testing)**: 3-4 hours
- **Phase 7 (Documentation)**: 2 hours
- **Phase 8 (Validation)**: 1 hour

**Total**: 16-22 hours (2-3 working days)

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Performance overhead > 5% | High | Implement sampling (10% in prod), async exporters |
| Trace data volume too large | Medium | Configure Jaeger retention, use sampling |
| Docker Compose complexity | Low | Provide clear setup docs, sensible defaults |
| Test flakiness (async traces) | Medium | Use in-memory exporters for unit tests, retries for integration tests |
| Backward compatibility break | High | Keep `OpenAIUsageMonitor`, feature flag for OTEL |

---

## Next Steps

1. Create feature branch: `feat/observability-opentelemetry`
2. Begin Phase 1: Add dependencies and create observability module
3. Follow TDD: write failing test → implement → refactor → commit
