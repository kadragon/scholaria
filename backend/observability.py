"""OpenTelemetry observability configuration for Scholaria backend."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio

if TYPE_CHECKING:
    from fastapi import FastAPI

    from backend.config import Settings

logger = logging.getLogger(__name__)


def setup_observability(app: FastAPI, settings: Settings) -> None:
    """
    Configure OpenTelemetry instrumentation for the application.

    Args:
        app: FastAPI application instance
        settings: Application settings

    Returns:
        None
    """
    if not settings.OTEL_ENABLED:
        logger.info("OpenTelemetry disabled via OTEL_ENABLED=false")
        return

    logger.info(
        "Initializing OpenTelemetry observability (service=%s)",
        settings.OTEL_SERVICE_NAME,
    )

    resource = Resource.create({"service.name": settings.OTEL_SERVICE_NAME})

    _setup_tracing(settings, resource)
    _setup_metrics(settings, resource)
    _setup_auto_instrumentation(app)

    logger.info("OpenTelemetry observability initialized successfully")


def _setup_tracing(settings: Settings, resource: Resource) -> None:
    """Configure distributed tracing with OTLP or console exporter."""
    provider = TracerProvider(
        resource=resource,
        sampler=ParentBasedTraceIdRatio(settings.OTEL_TRACES_SAMPLER_ARG),
    )

    if settings.DEBUG:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        logger.debug("Added ConsoleSpanExporter for development")

    try:
        otlp_exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        logger.info(
            "Added OTLPSpanExporter (endpoint=%s)", settings.OTEL_EXPORTER_OTLP_ENDPOINT
        )
    except Exception as e:
        logger.warning("Failed to configure OTLP exporter: %s", e)

    trace.set_tracer_provider(provider)


def _setup_metrics(settings: Settings, resource: Resource) -> None:
    """Configure Prometheus metrics collection."""
    if not settings.PROMETHEUS_METRICS_ENABLED:
        logger.info("Prometheus metrics disabled")
        return

    try:
        metric_reader = PrometheusMetricReader()
        provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(provider)

        logger.info("Prometheus metrics configured")
    except Exception as e:
        logger.warning("Failed to configure Prometheus metrics: %s", e)


def _setup_auto_instrumentation(app: FastAPI) -> None:
    """Configure automatic instrumentation for FastAPI, HTTPX, and Redis."""
    try:
        FastAPIInstrumentor.instrument_app(app)
        logger.debug("FastAPI auto-instrumentation enabled")
    except Exception as e:
        logger.warning("Failed to instrument FastAPI: %s", e)

    try:
        HTTPXClientInstrumentor().instrument()
        logger.debug("HTTPX client auto-instrumentation enabled")
    except Exception as e:
        logger.warning("Failed to instrument HTTPX: %s", e)

    try:
        RedisInstrumentor().instrument()
        logger.debug("Redis auto-instrumentation enabled")
    except Exception as e:
        logger.warning("Failed to instrument Redis: %s", e)


def get_tracer(name: str) -> trace.Tracer:
    """
    Get a tracer instance for manual instrumentation.

    Args:
        name: Name of the tracer (typically __name__)

    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)


def get_meter(name: str) -> metrics.Meter:
    """
    Get a meter instance for custom metrics.

    Args:
        name: Name of the meter (typically __name__)

    Returns:
        Meter instance
    """
    return metrics.get_meter(name)
