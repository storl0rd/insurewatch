"""
instrumentation.py - Initialize OpenTelemetry before anything else

LAB 4 — FULL CHAOS (combined challenges)
This service has THREE problems to find and fix:

  PROBLEM 1 — PROPAGATOR MISMATCH
    This service uses B3 propagation. All other services use W3C TraceContext.
    Traces break at every boundary where this service sends or receives context.

  PROBLEM 2 — MISSING AUTO-INSTRUMENTATION
    PymongoInstrumentor, HTTPXClientInstrumentor, and LoggingInstrumentor
    have been removed. Database calls, outgoing HTTP, and log correlation are
    all invisible.

  PROBLEM 3 — INCOMPLETE COLLECTOR CONFIG
    All services send to the OTel Collector (collector:4318), but the collector
    pipeline in collector/skeleton.yml is incomplete. No data reaches Grafana
    until you complete the config.

Approach:
  - Start with Problem 3 (get data flowing at all)
  - Then fix Problem 1 (connect the trace chain)
  - Then fix Problem 2 (fill in the instrumentation gaps)
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
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.propagate import set_global_textmap

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

# PROBLEM 1: B3 propagator — incompatible with W3C TraceContext used everywhere else
set_global_textmap(B3MultiFormat())

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

# PROBLEM 2: Auto-instrumentations REMOVED
# TODO: from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
# TODO: from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
# TODO: from opentelemetry.instrumentation.logging import LoggingInstrumentor
# TODO: PymongoInstrumentor().instrument()
# TODO: HTTPXClientInstrumentor().instrument()
# TODO: LoggingInstrumentor().instrument(set_logging_format=True)

handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
