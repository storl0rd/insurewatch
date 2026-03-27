"""
instrumentation.py - Initialize OpenTelemetry before anything else

LAB 2 — MISSING INSTRUMENTATION
The TracerProvider, MeterProvider, and LoggerProvider are configured and
exported to the LGTM stack. The SDK pipeline is healthy.

However, the auto-instrumentation libraries (FastAPI, pymongo, httpx) have
been intentionally removed. The manual spans in main.py have also been
removed.

Result: claims-service will appear healthy but generate zero spans. You
will see the service in the service map only if other services call it,
but there will be no visibility into what happens inside claims-service.

Your tasks:
  1. Re-add the auto-instrumentors below (FastAPIInstrumentor goes in main.py)
  2. Add a manual span around the submit_claim handler in main.py
  3. Add span attributes for claim.type, claim.amount, claim.status
  4. Verify traces appear in Grafana Tempo

Hint: auto-instrumentors must be called before the app starts handling requests.
"""
import os
import logging
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
OTLP_HEADERS = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")

headers = {}
if OTLP_HEADERS:
    for header in OTLP_HEADERS.split(','):
        if '=' in header:
            key, value = header.split('=', 1)
            headers[key.strip()] = value.strip()

resource = Resource.create({
    "service.name": "claims-service",
    "service.version": "1.0.0",
    "deployment.environment": os.getenv("ENVIRONMENT", "production"),
    "service.language": "python",
})

# Traces
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{OTLP_ENDPOINT}/v1/traces", headers=headers))
)
trace.set_tracer_provider(tracer_provider)

# Metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=f"{OTLP_ENDPOINT}/v1/metrics", headers=headers),
    export_interval_millis=10000,
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

# Logs
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(
        OTLPLogExporter(endpoint=f"{OTLP_ENDPOINT}/v1/logs", headers=headers)
    )
)

# LAB 2: Auto-instrumentations REMOVED — add them back!
# TODO: PymongoInstrumentor().instrument()
# TODO: HTTPXClientInstrumentor().instrument()
# TODO: LoggingInstrumentor().instrument(set_logging_format=True)

handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
