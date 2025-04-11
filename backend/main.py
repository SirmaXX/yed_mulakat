from fastapi import FastAPI, Request, HTTPException
import numpy as np
from pydantic import BaseModel
from typing import List
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from tensorflow.keras.models import load_model
import os

# Initialize tracing
resource = Resource.create(
    {"service.name": os.getenv("OTEL_SERVICE_NAME", "fastapi-service")}
)
provider = TracerProvider(resource=resource)

# Use OTLP exporter with environment variables
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
    insecure=True,
)

provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)


from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, default_limits=["1/minute"])

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
#  app.add_middleware(TrustedHostMiddleware, allowed_hosts=[""] )


SOC_model = load_model("models/SOC_LSTM.h5")  # soc modeli
SOH_model = load_model("models/SOH_LSTM.h5")  # soh modeli


@app.get("/")
async def read_root():
    return {"message": "Hello World"}


@app.get("/test-limiter")
@limiter.limit("5/minute")
async def test_limiter(request: Request):
    return {"message": "Hello limiter"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, request: Request):
    current_span = trace.get_current_span()
    current_span.set_attribute("item_id", item_id)

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("custom_operation"):
        result = {"item_id": item_id, "q": request.query_params.get("q")}

    return result


class TimeStepData(BaseModel):
    voltage_measured: float
    current_measured: float
    temperature_measured: float
    current_load: float
    voltage_load: float
    time: float


class PredictionRequest(BaseModel):
    ambient_temperature: float = 24.0  # Varsayılan değer
    rul: int = 167  # Varsayılan değer
    time_steps: List[TimeStepData]  # 10 adet zaman adımı


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
    tahmin = SOH_model.predict(manuel_veri)

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
    return {"predicted_soc": float(tahmin[0][0])}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
