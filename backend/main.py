from fastapi import FastAPI, Request, HTTPException
import numpy as np
from pydantic import BaseModel
from typing import List
import os
from app.main import create_app
from fastapi.middleware.cors import CORSMiddleware

# Monitoring ve Observability için importlar
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider


# Rate limiting için
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
import time


def setup_observability():
    # Tracing konfigürasyonu
    resource = Resource.create(
        {"service.name": os.getenv("OTEL_SERVICE_NAME", "fastapi-service")}
    )
    trace_provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        insecure=True,
    )
    trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(trace_provider)

    # Metrikler için MeterProvider
    metrics.set_meter_provider(MeterProvider())


# FastAPI uygulamasını başlat
app = create_app()
setup_observability()
FastAPIInstrumentor.instrument_app(app)

# Rate limiting konfigürasyonu
# limiter = Limiter(key_func=get_remote_address, default_limits=["1/minute"])
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# app.add_middleware(SlowAPIMiddleware)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # geliştirme için geniş tut, prod’da daralt
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Metrikler ve tracing için yardımcı fonksiyonlar
def record_metrics(endpoint: str, duration: float, status_code: int):
    meter = metrics.get_meter(__name__)
    request_counter = meter.create_counter(
        "http_requests_total", description="Total HTTP requests", unit="1"
    )
    request_counter.add(1, {"endpoint": endpoint, "status_code": str(status_code)})

    latency_histogram = meter.create_histogram(
        "http_request_duration_seconds",
        description="HTTP request duration in seconds",
        unit="s",
    )
    latency_histogram.record(duration, {"endpoint": endpoint})


# Middleware for metrics
@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    record_metrics(
        endpoint=str(request.url.path),
        duration=process_time,
        status_code=response.status_code,
    )

    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
