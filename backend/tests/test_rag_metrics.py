"""
Tests for RAG pipeline metrics collection.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

from backend.services.rag_service import AsyncRAGService


@pytest.fixture(autouse=True)
def disable_otel(monkeypatch):
    """Disable OTEL for tests to avoid provider conflicts."""
    monkeypatch.setenv("OTEL_ENABLED", "false")


@pytest.fixture
def setup_metrics():
    """Setup metrics for testing."""
    reader = InMemoryMetricReader()
    provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(provider)
    return reader


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    return AsyncMock()


@pytest.fixture
def async_rag_service(mock_redis, monkeypatch, setup_metrics):
    """Create AsyncRAGService with mocked dependencies."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    with patch("backend.services.rag_service.QdrantService"):
        service = AsyncRAGService(
            redis_client=mock_redis,
            openai_api_key="test-key",
            openai_chat_model="gpt-4o-mini",
            rag_search_limit=10,
            rag_rerank_top_k=5,
        )
        return service


@pytest.mark.asyncio
async def test_rag_query_duration_metric(setup_metrics, async_rag_service, mock_redis):
    """Test that rag_query_duration_seconds histogram is recorded."""
    # Mock dependencies
    mock_redis.get.return_value = None
    async_rag_service.embedding_service.generate_embedding = MagicMock(
        return_value=[0.1] * 1536
    )
    async_rag_service.qdrant_service.search_similar = MagicMock(return_value=[])
    async_rag_service.reranking_service.rerank_results = MagicMock(return_value=[])
    async_rag_service._generate_answer = AsyncMock(
        return_value=("Test answer", {"prompt_tokens": 100, "completion_tokens": 50})
    )

    # Execute query
    await async_rag_service.query("test question", topic_ids=[1])

    # Verify metric was recorded
    metrics_data = setup_metrics.get_metrics_data()
    metric_names = [
        metric.name
        for resource_metrics in metrics_data.resource_metrics
        for scope_metrics in resource_metrics.scope_metrics
        for metric in scope_metrics.metrics
    ]

    assert "rag.query.duration" in metric_names


@pytest.mark.asyncio
async def test_embedding_cache_hit_metric(setup_metrics, async_rag_service, mock_redis):
    """Test that rag_embedding_cache_hits_total counter is incremented."""
    # Mock cache hit
    async_rag_service.embedding_service.cache.get = MagicMock(return_value=[0.1] * 1536)

    # Generate embedding (should hit cache)
    async_rag_service.embedding_service.generate_embedding("test text")

    # Verify metric was recorded
    metrics_data = setup_metrics.get_metrics_data()
    metric_names = [
        metric.name
        for resource_metrics in metrics_data.resource_metrics
        for scope_metrics in resource_metrics.scope_metrics
        for metric in scope_metrics.metrics
    ]

    assert "rag.embedding.cache.hits" in metric_names


@pytest.mark.asyncio
async def test_embedding_cache_miss_metric(setup_metrics, async_rag_service):
    """Test that rag_embedding_cache_misses_total counter is incremented."""
    # Mock cache miss and OpenAI API call
    async_rag_service.embedding_service.cache.get = MagicMock(return_value=None)
    async_rag_service.embedding_service.client.embeddings.create = MagicMock(
        return_value=MagicMock(
            data=[MagicMock(embedding=[0.1] * 1536)],
            usage=MagicMock(total_tokens=100),
        )
    )

    # Generate embedding (should miss cache)
    async_rag_service.embedding_service.generate_embedding("test text")

    # Verify metric was recorded
    metrics_data = setup_metrics.get_metrics_data()
    metric_names = [
        metric.name
        for resource_metrics in metrics_data.resource_metrics
        for scope_metrics in resource_metrics.scope_metrics
        for metric in scope_metrics.metrics
    ]

    assert "rag.embedding.cache.misses" in metric_names


@pytest.mark.asyncio
async def test_openai_tokens_metric(setup_metrics, async_rag_service, mock_redis):
    """Test that rag_openai_tokens_total counter is incremented."""
    # Mock dependencies
    mock_redis.get.return_value = None
    async_rag_service.embedding_service.generate_embedding = MagicMock(
        return_value=[0.1] * 1536
    )
    async_rag_service.qdrant_service.search_similar = MagicMock(return_value=[])
    async_rag_service.reranking_service.rerank_results = MagicMock(return_value=[])
    async_rag_service._generate_answer = AsyncMock(
        return_value=("Test answer", {"prompt_tokens": 100, "completion_tokens": 50})
    )

    # Execute query
    await async_rag_service.query("test question", topic_ids=[1])

    # Verify metric was recorded
    metrics_data = setup_metrics.get_metrics_data()
    metric_names = [
        metric.name
        for resource_metrics in metrics_data.resource_metrics
        for scope_metrics in resource_metrics.scope_metrics
        for metric in scope_metrics.metrics
    ]

    assert "rag.openai.tokens" in metric_names


@pytest.mark.asyncio
async def test_vector_search_results_metric(
    setup_metrics, async_rag_service, mock_redis
):
    """Test that rag_vector_search_results_count histogram is recorded."""
    # Mock dependencies
    mock_redis.get.return_value = None
    async_rag_service.embedding_service.generate_embedding = MagicMock(
        return_value=[0.1] * 1536
    )
    async_rag_service.qdrant_service.search_similar = MagicMock(
        return_value=[
            {"id": 1, "score": 0.9},
            {"id": 2, "score": 0.8},
            {"id": 3, "score": 0.7},
        ]
    )
    async_rag_service.reranking_service.rerank_results = MagicMock(
        return_value=[
            {"id": 1, "score": 0.95},
        ]
    )
    async_rag_service._generate_answer = AsyncMock(
        return_value=("Test answer", {"prompt_tokens": 100, "completion_tokens": 50})
    )

    # Execute query
    await async_rag_service.query("test question", topic_ids=[1])

    # Verify metric was recorded
    metrics_data = setup_metrics.get_metrics_data()
    metric_names = [
        metric.name
        for resource_metrics in metrics_data.resource_metrics
        for scope_metrics in resource_metrics.scope_metrics
        for metric in scope_metrics.metrics
    ]

    assert "rag.vector_search.results" in metric_names


@pytest.mark.asyncio
async def test_query_error_metric(setup_metrics, async_rag_service, mock_redis):
    """Test that rag_query_errors_total counter is incremented on error."""
    # Mock dependencies to raise error
    mock_redis.get.return_value = None
    async_rag_service.embedding_service.generate_embedding = MagicMock(
        side_effect=ValueError("Test error")
    )

    # Execute query (should fail)
    with pytest.raises(ValueError):
        await async_rag_service.query("test question", topic_ids=[1])

    # Verify metric was recorded
    metrics_data = setup_metrics.get_metrics_data()
    metric_names = [
        metric.name
        for resource_metrics in metrics_data.resource_metrics
        for scope_metrics in resource_metrics.scope_metrics
        for metric in scope_metrics.metrics
    ]

    assert "rag.query.errors" in metric_names
