"""
OpenTelemetry Integration for Observability
Provides tracing, metrics, and logging for the marketing platform
"""

import os
import time
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional

from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger("telemetry")

# Try to import OpenTelemetry
OTEL_AVAILABLE = False
try:
    from opentelemetry import metrics, trace
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import (
        ConsoleMetricExporter,
        PeriodicExportingMetricReader,
    )
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.semconv.resource import ResourceAttributes
    from opentelemetry.trace import Status, StatusCode

    OTEL_AVAILABLE = True
except ImportError:
    logger.info("OpenTelemetry not installed, using fallback telemetry")

# Try to import OTLP exporters
OTLP_AVAILABLE = False
try:
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

    OTLP_AVAILABLE = True
except ImportError:
    pass


class FallbackSpan:
    """Fallback span for when OpenTelemetry is not available"""

    def __init__(self, name: str):
        self.name = name
        self.attributes: Dict[str, Any] = {}
        self.start_time = time.time()

    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value

    def set_status(self, status):
        self.attributes["status"] = str(status)

    def record_exception(self, exception: Exception):
        self.attributes["exception"] = str(exception)

    def add_event(self, name: str, attributes: Optional[Dict] = None):
        logger.debug(f"Span event: {name}", extra=attributes or {})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.time() - self.start_time) * 1000
        logger.debug(
            f"Span completed: {self.name}",
            extra={"duration_ms": round(duration, 2), **self.attributes},
        )
        return False


class FallbackTracer:
    """Fallback tracer for when OpenTelemetry is not available"""

    def __init__(self, name: str):
        self.name = name

    @contextmanager
    def start_as_current_span(self, name: str, **kwargs):
        span = FallbackSpan(name)
        try:
            yield span
        except Exception as e:
            span.record_exception(e)
            raise


class FallbackMeter:
    """Fallback meter for when OpenTelemetry is not available"""

    def __init__(self, name: str):
        self.name = name
        self._counters: Dict[str, int] = {}
        self._histograms: Dict[str, list] = {}

    def create_counter(self, name: str, description: str = "", unit: str = ""):
        return FallbackCounter(name, self._counters)

    def create_histogram(self, name: str, description: str = "", unit: str = ""):
        return FallbackHistogram(name, self._histograms)

    def create_up_down_counter(self, name: str, description: str = "", unit: str = ""):
        return FallbackCounter(name, self._counters)


class FallbackCounter:
    def __init__(self, name: str, storage: Dict):
        self.name = name
        self._storage = storage
        self._storage[name] = 0

    def add(self, amount: int, attributes: Optional[Dict] = None):
        self._storage[self.name] += amount


class FallbackHistogram:
    def __init__(self, name: str, storage: Dict):
        self.name = name
        self._storage = storage
        self._storage[name] = []

    def record(self, value: float, attributes: Optional[Dict] = None):
        self._storage[self.name].append(value)


class Telemetry:
    """
    Telemetry manager for the marketing platform.
    Provides tracing and metrics with fallback when OTEL is not available.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.service_name = os.getenv("OTEL_SERVICE_NAME", "randols-marketing")
        self._tracer = None
        self._meter = None

        self._setup_telemetry()
        self._initialized = True

    def _setup_telemetry(self):
        """Initialize OpenTelemetry if available"""
        if not OTEL_AVAILABLE:
            logger.info("Using fallback telemetry (OpenTelemetry not installed)")
            self._tracer = FallbackTracer(self.service_name)
            self._meter = FallbackMeter(self.service_name)
            return

        # Create resource
        resource = Resource.create(
            {
                ResourceAttributes.SERVICE_NAME: self.service_name,
                ResourceAttributes.SERVICE_VERSION: "1.0.0",
                "deployment.environment": os.getenv("FLASK_ENV", "development"),
            }
        )

        # Setup tracer
        tracer_provider = TracerProvider(resource=resource)

        # Add exporters based on configuration
        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if endpoint and OTLP_AVAILABLE:
            # Use OTLP exporter for production
            otlp_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
            tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            logger.info(f"OTLP trace exporter configured: {endpoint}")
        else:
            # Use console exporter for development (only if verbose logging)
            if os.getenv("VERBOSE_LOGGING", "").lower() == "true":
                tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        trace.set_tracer_provider(tracer_provider)
        self._tracer = trace.get_tracer(self.service_name)

        # Setup meter
        metric_readers = []
        if endpoint and OTLP_AVAILABLE:
            otlp_metric_exporter = OTLPMetricExporter(endpoint=endpoint, insecure=True)
            metric_readers.append(
                PeriodicExportingMetricReader(otlp_metric_exporter, export_interval_millis=60000)
            )
        elif os.getenv("VERBOSE_LOGGING", "").lower() == "true":
            metric_readers.append(
                PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=60000)
            )

        if metric_readers:
            meter_provider = MeterProvider(resource=resource, metric_readers=metric_readers)
            metrics.set_meter_provider(meter_provider)
            self._meter = metrics.get_meter(self.service_name)
        else:
            self._meter = FallbackMeter(self.service_name)

        logger.info("OpenTelemetry initialized")

    @property
    def tracer(self):
        """Get the tracer instance"""
        return self._tracer

    @property
    def meter(self):
        """Get the meter instance"""
        return self._meter

    def span(self, name: str, **kwargs):
        """Create a new span context manager"""
        return self._tracer.start_as_current_span(name, **kwargs)


# Global telemetry instance
_telemetry: Optional[Telemetry] = None


def get_telemetry() -> Telemetry:
    """Get the global telemetry instance"""
    global _telemetry
    if _telemetry is None:
        _telemetry = Telemetry()
    return _telemetry


def get_tracer():
    """Get the global tracer"""
    return get_telemetry().tracer


def get_meter():
    """Get the global meter"""
    return get_telemetry().meter


# Convenience decorators


def traced(name: Optional[str] = None, attributes: Optional[Dict] = None):
    """
    Decorator to trace a function.

    Usage:
        @traced("my_operation")
        def my_function():
            pass
    """

    def decorator(func: Callable) -> Callable:
        span_name = name or f"{func.__module__}.{func.__name__}"

        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(span_name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                try:
                    result = func(*args, **kwargs)
                    if OTEL_AVAILABLE:
                        span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    if OTEL_AVAILABLE:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(span_name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                try:
                    result = await func(*args, **kwargs)
                    if OTEL_AVAILABLE:
                        span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    if OTEL_AVAILABLE:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    return decorator


def timed(metric_name: str, unit: str = "ms"):
    """
    Decorator to record function execution time as a metric.

    Usage:
        @timed("content_generation_duration")
        def generate_content():
            pass
    """

    def decorator(func: Callable) -> Callable:
        meter = get_meter()
        histogram = meter.create_histogram(
            metric_name, description=f"Duration of {func.__name__}", unit=unit
        )

        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = (time.time() - start) * 1000  # Convert to ms
                histogram.record(duration, {"function": func.__name__})

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                duration = (time.time() - start) * 1000
                histogram.record(duration, {"function": func.__name__})

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    return decorator


# Pre-defined metrics for the marketing platform
class MarketingMetrics:
    """Pre-defined metrics for the marketing platform"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        meter = get_meter()

        # Content metrics
        self.content_generated = meter.create_counter(
            "content_generated_total", description="Total content items generated", unit="1"
        )
        self.content_approved = meter.create_counter(
            "content_approved_total", description="Total content items approved", unit="1"
        )
        self.content_rejected = meter.create_counter(
            "content_rejected_total", description="Total content items rejected", unit="1"
        )

        # LLM metrics
        self.llm_requests = meter.create_counter(
            "llm_requests_total", description="Total LLM API requests", unit="1"
        )
        self.llm_tokens = meter.create_counter(
            "llm_tokens_total", description="Total tokens used", unit="1"
        )
        self.llm_cost = meter.create_counter(
            "llm_cost_total", description="Total LLM cost in USD cents", unit="cents"
        )
        self.llm_latency = meter.create_histogram(
            "llm_request_duration", description="LLM request duration", unit="ms"
        )

        # Posting metrics
        self.posts_scheduled = meter.create_counter(
            "posts_scheduled_total", description="Total posts scheduled", unit="1"
        )
        self.posts_published = meter.create_counter(
            "posts_published_total", description="Total posts published", unit="1"
        )
        self.posts_failed = meter.create_counter(
            "posts_failed_total", description="Total posts that failed to publish", unit="1"
        )

        # Agent metrics
        self.agent_active = meter.create_up_down_counter(
            "agents_active", description="Number of active agents", unit="1"
        )

        self._initialized = True

    def record_content_generated(self, content_type: str, platform: str):
        self.content_generated.add(1, {"content_type": content_type, "platform": platform})

    def record_content_approved(self, content_type: str):
        self.content_approved.add(1, {"content_type": content_type})

    def record_content_rejected(self, content_type: str, reason: str):
        self.content_rejected.add(1, {"content_type": content_type, "reason": reason})

    def record_llm_request(self, model: str, tokens: int, cost_usd: float, latency_ms: float):
        self.llm_requests.add(1, {"model": model})
        self.llm_tokens.add(tokens, {"model": model})
        self.llm_cost.add(int(cost_usd * 100), {"model": model})  # Convert to cents
        self.llm_latency.record(latency_ms, {"model": model})

    def record_post_scheduled(self, platform: str):
        self.posts_scheduled.add(1, {"platform": platform})

    def record_post_published(self, platform: str):
        self.posts_published.add(1, {"platform": platform})

    def record_post_failed(self, platform: str, error: str):
        self.posts_failed.add(1, {"platform": platform, "error": error})


def get_marketing_metrics() -> MarketingMetrics:
    """Get the marketing metrics singleton"""
    return MarketingMetrics()
