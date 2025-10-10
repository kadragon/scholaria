"""
Tests for OpenAIUsageMonitor OTel metrics integration.
"""

from opentelemetry import metrics as otel_metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

from backend.retrieval.monitoring import OpenAIUsageMonitor


def test_track_embedding_usage_records_otel_metrics():
    """Test that track_embedding_usage records OTel counter metrics."""
    reader = InMemoryMetricReader()
    provider = MeterProvider(metric_readers=[reader])
    otel_metrics.set_meter_provider(provider)

    monitor = OpenAIUsageMonitor()
    monitor.track_embedding_usage(tokens=100, model="text-embedding-3-large")

    metrics_data = reader.get_metrics_data()
    if metrics_data and metrics_data.resource_metrics:
        metric_names = [
            metric.name
            for resource_metrics in metrics_data.resource_metrics
            for scope_metrics in resource_metrics.scope_metrics
            for metric in scope_metrics.metrics
        ]

        assert "rag.openai.embedding.calls" in metric_names
        assert "rag.openai.embedding.tokens" in metric_names


def test_track_chat_completion_usage_records_otel_metrics():
    """Test that track_chat_completion_usage records OTel counter metrics."""
    reader = InMemoryMetricReader()
    provider = MeterProvider(metric_readers=[reader])
    otel_metrics.set_meter_provider(provider)

    monitor = OpenAIUsageMonitor()
    monitor.track_chat_completion_usage(
        prompt_tokens=100, completion_tokens=50, model="gpt-4o-mini"
    )

    metrics_data = reader.get_metrics_data()
    if metrics_data and metrics_data.resource_metrics:
        metric_names = [
            metric.name
            for resource_metrics in metrics_data.resource_metrics
            for scope_metrics in resource_metrics.scope_metrics
            for metric in scope_metrics.metrics
        ]

        assert "rag.openai.chat.calls" in metric_names
        assert "rag.openai.chat.tokens" in metric_names


def test_otel_metrics_have_correct_attributes():
    """Test that OTel metrics include model and type attributes."""
    reader = InMemoryMetricReader()
    provider = MeterProvider(metric_readers=[reader])
    otel_metrics.set_meter_provider(provider)

    monitor = OpenAIUsageMonitor()
    monitor.track_embedding_usage(tokens=100, model="text-embedding-3-large")
    monitor.track_chat_completion_usage(
        prompt_tokens=100, completion_tokens=50, model="gpt-4o-mini"
    )

    metrics_data = reader.get_metrics_data()
    if metrics_data and metrics_data.resource_metrics:
        for resource_metrics in metrics_data.resource_metrics:
            for scope_metrics in resource_metrics.scope_metrics:
                for metric in scope_metrics.metrics:
                    if metric.name == "rag.openai.embedding.tokens":
                        for data_point in metric.data.data_points:
                            assert (
                                data_point.attributes.get("model")
                                == "text-embedding-3-large"
                            )
                    elif metric.name == "rag.openai.chat.tokens":
                        for data_point in metric.data.data_points:
                            assert data_point.attributes.get("model") == "gpt-4o-mini"
                            assert data_point.attributes.get("type") in [
                                "prompt",
                                "completion",
                            ]
