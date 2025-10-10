"""Tests for OpenTelemetry observability module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from opentelemetry import metrics, trace

from backend.config import Settings
from backend.observability import get_meter, get_tracer, setup_observability


def test_setup_observability_when_disabled():
    """Test that observability setup is skipped when OTEL_ENABLED=false."""
    app = FastAPI()
    settings = Settings(OTEL_ENABLED=False)

    with patch("backend.observability.logger") as mock_logger:
        setup_observability(app, settings)
        mock_logger.info.assert_called_once_with(
            "OpenTelemetry disabled via OTEL_ENABLED=false"
        )


def test_setup_observability_initializes_tracer_provider():
    """Test that setup_observability initializes TracerProvider."""
    app = FastAPI()
    settings = Settings(
        OTEL_ENABLED=True,
        OTEL_SERVICE_NAME="test-service",
        DEBUG=False,
    )

    with patch("backend.observability.trace.set_tracer_provider") as mock_set_tracer:
        setup_observability(app, settings)
        mock_set_tracer.assert_called_once()
        args = mock_set_tracer.call_args[0]
        provider = args[0]
        assert provider.resource.attributes["service.name"] == "test-service"


def test_setup_observability_configures_console_exporter_in_debug():
    """Test that console exporter is added in DEBUG mode."""
    app = FastAPI()
    settings = Settings(
        OTEL_ENABLED=True,
        DEBUG=True,
    )

    with (
        patch(
            "backend.observability.ConsoleSpanExporter"
        ) as mock_console_exporter_class,
        patch("backend.observability.BatchSpanProcessor") as mock_processor_class,
    ):
        setup_observability(app, settings)
        mock_console_exporter_class.assert_called_once()
        assert mock_processor_class.call_count >= 1


def test_setup_observability_configures_otlp_exporter():
    """Test that OTLP exporter is configured with correct endpoint."""
    app = FastAPI()
    settings = Settings(
        OTEL_ENABLED=True,
        OTEL_EXPORTER_OTLP_ENDPOINT="http://test-jaeger:4317",
        DEBUG=False,
    )

    with patch("backend.observability.OTLPSpanExporter") as mock_otlp_exporter_class:
        setup_observability(app, settings)
        mock_otlp_exporter_class.assert_called_once_with(
            endpoint="http://test-jaeger:4317"
        )


def test_setup_observability_handles_otlp_exporter_failure():
    """Test that setup continues gracefully if OTLP exporter fails."""
    app = FastAPI()
    settings = Settings(
        OTEL_ENABLED=True,
        DEBUG=False,
    )

    with (
        patch(
            "backend.observability.OTLPSpanExporter",
            side_effect=Exception("Connection failed"),
        ),
        patch("backend.observability.logger") as mock_logger,
    ):
        setup_observability(app, settings)
        assert any(
            "Failed to configure OTLP exporter" in str(call)
            for call in mock_logger.warning.call_args_list
        )


def test_setup_observability_configures_prometheus_metrics():
    """Test that Prometheus metrics are configured when enabled."""
    app = FastAPI()
    settings = Settings(
        OTEL_ENABLED=True,
        PROMETHEUS_METRICS_ENABLED=True,
        DEBUG=False,
    )

    with (
        patch("backend.observability.PrometheusMetricReader") as mock_reader_class,
        patch("backend.observability.metrics.set_meter_provider") as mock_set_meter,
    ):
        setup_observability(app, settings)
        mock_reader_class.assert_called_once()
        mock_set_meter.assert_called_once()


def test_setup_observability_skips_metrics_when_disabled():
    """Test that metrics setup is skipped when PROMETHEUS_METRICS_ENABLED=false."""
    app = FastAPI()
    settings = Settings(
        OTEL_ENABLED=True,
        PROMETHEUS_METRICS_ENABLED=False,
        DEBUG=False,
    )

    with patch("backend.observability.logger") as mock_logger:
        setup_observability(app, settings)
        assert any(
            "Prometheus metrics disabled" in str(call)
            for call in mock_logger.info.call_args_list
        )


def test_setup_observability_instruments_fastapi():
    """Test that FastAPI auto-instrumentation is applied."""
    app = FastAPI()
    settings = Settings(
        OTEL_ENABLED=True,
        DEBUG=False,
    )

    with patch(
        "backend.observability.FastAPIInstrumentor.instrument_app"
    ) as mock_instrument:
        setup_observability(app, settings)
        mock_instrument.assert_called_once_with(app)


def test_setup_observability_instruments_httpx():
    """Test that HTTPX auto-instrumentation is applied."""
    app = FastAPI()
    settings = Settings(
        OTEL_ENABLED=True,
        DEBUG=False,
    )

    with patch(
        "backend.observability.HTTPXClientInstrumentor"
    ) as mock_instrumentor_class:
        mock_instrumentor = MagicMock()
        mock_instrumentor_class.return_value = mock_instrumentor

        setup_observability(app, settings)
        mock_instrumentor.instrument.assert_called_once()


def test_setup_observability_instruments_redis():
    """Test that Redis auto-instrumentation is applied."""
    app = FastAPI()
    settings = Settings(
        OTEL_ENABLED=True,
        DEBUG=False,
    )

    with patch("backend.observability.RedisInstrumentor") as mock_instrumentor_class:
        mock_instrumentor = MagicMock()
        mock_instrumentor_class.return_value = mock_instrumentor

        setup_observability(app, settings)
        mock_instrumentor.instrument.assert_called_once()


def test_get_tracer_returns_tracer_instance():
    """Test that get_tracer returns a valid Tracer instance."""
    tracer = get_tracer("test_module")
    assert tracer is not None
    assert isinstance(tracer, trace.Tracer)


def test_get_meter_returns_meter_instance():
    """Test that get_meter returns a valid Meter instance."""
    meter = get_meter("test_module")
    assert meter is not None
    assert isinstance(meter, metrics.Meter)


def test_setup_observability_applies_sampling():
    """Test that sampling configuration is applied."""
    app = FastAPI()
    settings = Settings(
        OTEL_ENABLED=True,
        OTEL_TRACES_SAMPLER_ARG=0.1,
        DEBUG=False,
    )

    with patch("backend.observability.ParentBasedTraceIdRatio") as mock_sampler_class:
        setup_observability(app, settings)
        mock_sampler_class.assert_called_once_with(0.1)
