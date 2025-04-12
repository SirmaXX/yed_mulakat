from fastapi import FastAPI, Request, HTTPException
import numpy as np
from pydantic import BaseModel
from typing import List
import os
from tensorflow.keras.models import load_model

# Monitoring ve Observability için importlar
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from prometheus_client import start_http_server
from prometheus_fastapi_instrumentator import Instrumentator

# Rate limiting için
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
import time

# Modelleri yükle
SOC_model = load_model("models/SOC_LSTM.h5")
SOH_model = load_model("models/SOH_LSTM.h5")


# OpenTelemetry ve Prometheus başlatma
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

    # Metrikler konfigürasyonu
    reader = PrometheusMetricReader()
    meter_provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)

    # Prometheus metrik sunucusu
    start_http_server(port=8001)


# FastAPI uygulamasını başlat
app = FastAPI()
setup_observability()
FastAPIInstrumentor.instrument_app(app)

# Rate limiting konfigürasyonu
limiter = Limiter(key_func=get_remote_address, default_limits=["1/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Prometheus instrumentator
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app).expose(app)


# Modeller için veri yapıları
class TimeStepData(BaseModel):
    voltage_measured: float
    current_measured: float
    temperature_measured: float
    current_load: float
    voltage_load: float
    time: float


class PredictionRequest(BaseModel):
    ambient_temperature: float = 24.0
    rul: int = 167
    time_steps: List[TimeStepData]


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


# API endpoint'leri


@app.get(
    "/predict-soc/",
    response_model=dict,
    description="Test için örnek veri ile soh için  tahmin yapar",
)
async def predict_soc(request: PredictionRequest):
    try:
        # Giriş verisini numpy array'e dönüştürme
        manuel_veri = []
        for ts in request.time_steps:
            manuel_veri.append(
                [
                    request.ambient_temperature,
                    ts.voltage_measured,
                    ts.current_measured,
                    ts.temperature_measured,
                    ts.current_load,
                    ts.voltage_load,
                    ts.time,
                    request.rul,
                ]
            )

        manuel_veri = np.array(manuel_veri).reshape(1, 10, 8)

        # Tahmin yapma
        tahmin = SOC_model.predict(manuel_veri)

        return {"predicted_soc": float(tahmin[0][0]), "input_data": request.dict()}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Örnek kullanım için test endpointi
@app.get(
    "/soc-test-predict/", description="Test için örnek veri ile soc için  tahmin yapar"
)
async def soh_test_predict():
    manuel_veri = np.array(
        [
            # [ambient_temp, voltage_measured, current_measured, temp_measured, current_load, voltage_load, time]
            [24.0, 4.19, -0.004, 24.33, -0.0006, 0.0, 0.0, 167],  # t1
            [24.0, 4.19, -0.001, 24.32, -0.0006, 4.2, 16.7, 167],  # t2
            [24.0, 3.25, -0.001, 35.29, -0.0006, 0.0, 3608.5, 167],  # t3
            [24.0, 3.26, -0.001, 35.02, -0.0006, 0.0, 3628.9, 167],  # t4
            [24.0, 3.26, -0.000, 34.75, -0.0006, 0.0, 3649.3, 167],  # t5
            [24.0, 3.27, -0.000, 34.49, -0.0006, 0.0, 3669.8, 167],  # t6
            [24.0, 3.27, -0.006, 34.23, -0.0006, 0.0, 3690.2, 167],  # t7
            [
                24.0,
                3.27,
                -0.006,
                34.23,
                -0.0006,
                0.0,
                3690.2,
                167,
            ],  # t8 (eksik veri için tekrar)
            [24.0, 3.27, -0.006, 34.23, -0.0006, 0.0, 3690.2, 167],  # t9
            [24.0, 3.27, -0.006, 34.23, -0.0006, 0.0, 3690.2, 167],  # t10
        ]
    )

    # Modelin beklediği şekle dönüştürme (1, 10, 8)
    manuel_veri = manuel_veri.reshape(1, 10, 8)

    # Tahmin yapma
    tahmin = SOC_model.predict(manuel_veri)

    return {"predicted_soc": float(tahmin[0][0])}


@app.get(
    "/predict-soh/",
    response_model=dict,
    description="Kullanıcıdan gelen veri üzerinden ,soh ile  tahmin yapar",
)
async def predict_soh(request: PredictionRequest):
    try:
        # Giriş verisini numpy array'e dönüştürme
        manuel_veri = []
        for ts in request.time_steps:
            manuel_veri.append(
                [
                    request.ambient_temperature,
                    ts.voltage_measured,
                    ts.current_measured,
                    ts.temperature_measured,
                    ts.current_load,
                    ts.voltage_load,
                    ts.time,
                    request.rul,
                ]
            )
        manuel_veri = np.array(manuel_veri).reshape(1, 10, 8)

        # Tahmin yapma
        tahmin = SOH_model.predict(manuel_veri)

        return {"predicted_soc": float(tahmin[0][0]), "input_data": request.dict()}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get(
    "/soh-test-predict/", description="Test için örnek veri ile soh için  tahmin yapar"
)
async def soc_test_predict(request: Request):
    manuel_veri = np.array(
        [
            # [ambient_temp, voltage_measured, current_measured, temp_measured, current_load, voltage_load, time]
            [24.0, 4.19, -0.004, 24.33, -0.0006, 0.0, 0.0, 167],  # t1
            [24.0, 4.19, -0.001, 24.32, -0.0006, 4.2, 16.7, 167],  # t2
            [24.0, 3.25, -0.001, 35.29, -0.0006, 0.0, 3608.5, 167],  # t3
            [24.0, 3.26, -0.001, 35.02, -0.0006, 0.0, 3628.9, 167],  # t4
            [24.0, 3.26, -0.000, 34.75, -0.0006, 0.0, 3649.3, 167],  # t5
            [24.0, 3.27, -0.000, 34.49, -0.0006, 0.0, 3669.8, 167],  # t6
            [24.0, 3.27, -0.006, 34.23, -0.0006, 0.0, 3690.2, 167],  # t7
            [
                24.0,
                3.27,
                -0.006,
                34.23,
                -0.0006,
                0.0,
                3690.2,
                167,
            ],  # t8 (eksik veri için tekrar)
            [24.0, 3.27, -0.006, 34.23, -0.0006, 0.0, 3690.2, 167],  # t9
            [24.0, 3.27, -0.006, 34.23, -0.0006, 0.0, 3690.2, 167],  # t10
        ]
    )

    # Modelin beklediği şekle dönüştürme (1, 10, 8)
    manuel_veri = manuel_veri.reshape(1, 10, 8)

    tahmin = SOH_model.predict(manuel_veri)
    return {"predicted_soh": float(tahmin[0][0])}


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
