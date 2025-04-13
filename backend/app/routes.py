from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pathlib import Path
import pandas as pd
import numpy as np
import os
from app.schemas import PredictionRequest
from opentelemetry import trace

battery_folder = Path(__file__).parent / "battery_datas"
soc_model_path = Path(__file__).parent / "models/SOC_LSTM.h5"
soh_model_path = Path(__file__).parent / "models/SOH_LSTM.h5"
SOC_model = load_model(soc_model_path)
SOH_model = load_model(soh_model_path)

api_router = APIRouter(responses={404: {"description": "Not found"}})


def trace_endpoint(request: Request, name: str):
    tracer = trace.get_tracer(__name__)
    span = trace.get_current_span()
    span.set_attribute("http.endpoint", str(request.url))
    return tracer.start_as_current_span(name)


@api_router.get(
    "/health", description="Servisin çalışıp çalışmadığını kontrol eden router"
)
async def health(req: Request):
    with trace_endpoint(req, "health-check"):
        return JSONResponse(content={"status": "ok"})


@api_router.get("/", description="index için router")
async def api_index(request: Request):
    with trace_endpoint(request, "api-index"):
        return {"message": "Hello from FastAPI!"}


@api_router.get("/items/{item_id}")
async def read_item(item_id: int, request: Request):
    current_span = trace.get_current_span()
    current_span.set_attribute("item_id", item_id)
    with trace_endpoint(request, "read-item"):
        return {"item_id": item_id, "q": request.query_params.get("q")}


@api_router.get(
    "/predict-soc/",
    response_model=dict,
    description="Test için örnek veri ile soh için  tahmin yapar",
)
async def predict_soc(request: PredictionRequest, req: Request):
    with trace_endpoint(req, "predict-soc"):
        try:
            manuel_veri = [
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
                for ts in request.time_steps
            ]
            manuel_veri = np.array(manuel_veri).reshape(1, 10, 8)
            tahmin = SOC_model.predict(manuel_veri)
            return {"predicted_soc": float(tahmin[0][0]), "input_data": request.dict()}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


@api_router.get(
    "/soc-test-predict/", description="Test için örnek veri ile soc için  tahmin yapar"
)
async def soh_test_predict(request: Request):
    with trace_endpoint(request, "soc-test-predict"):
        manuel_veri = np.array(
            [
                [24.0, 4.19, -0.004, 24.33, -0.0006, 0.0, 0.0, 167],
                [24.0, 4.19, -0.001, 24.32, -0.0006, 4.2, 16.7, 167],
                [24.0, 3.25, -0.001, 35.29, -0.0006, 0.0, 3608.5, 167],
                [24.0, 3.26, -0.001, 35.02, -0.0006, 0.0, 3628.9, 167],
                [24.0, 3.26, -0.000, 34.75, -0.0006, 0.0, 3649.3, 167],
                [24.0, 3.27, -0.000, 34.49, -0.0006, 0.0, 3669.8, 167],
                [24.0, 3.27, -0.006, 34.23, -0.0006, 0.0, 3690.2, 167],
                [24.0, 3.27, -0.006, 34.23, -0.0006, 0.0, 3690.2, 167],
                [24.0, 3.27, -0.006, 34.23, -0.0006, 0.0, 3690.2, 167],
                [24.0, 3.27, -0.006, 34.23, -0.0006, 0.0, 3690.2, 167],
            ]
        )
        manuel_veri = manuel_veri.reshape(1, 10, 8)
        tahmin = SOC_model.predict(manuel_veri)
        return {"predicted_soc": float(tahmin[0][0])}


@api_router.get(
    "/predict-soh/",
    response_model=dict,
    description="Kullanıcıdan gelen veri üzerinden ,soh ile  tahmin yapar",
)
async def predict_soh(request: PredictionRequest, req: Request):
    with trace_endpoint(req, "predict-soh"):
        try:
            manuel_veri = [
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
                for ts in request.time_steps
            ]
            manuel_veri = np.array(manuel_veri).reshape(1, 10, 8)
            tahmin = SOH_model.predict(manuel_veri)
            return {"predicted_soc": float(tahmin[0][0]), "input_data": request.dict()}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


@api_router.get(
    "/soh-test-predict/", description="Test için örnek veri ile soh için  tahmin yapar"
)
async def soc_test_predict(request: Request):
    with trace_endpoint(request, "soh-test-predict"):
        manuel_veri = np.array(
            [
                [24.0, 4.19, -0.004, 24.33, -0.0006, 0.0, 0.0, 167],
                [24.0, 4.19, -0.001, 24.32, -0.0006, 4.2, 16.7, 167],
                [24.0, 3.25, -0.001, 35.29, -0.0006, 0.0, 3608.5, 167],
                [24.0, 3.26, -0.001, 35.02, -0.0006, 0.0, 3628.9, 167],
                [24.0, 3.26, -0.000, 34.75, -0.0006, 0.0, 3649.3, 167],
                [24.0, 3.27, -0.000, 34.49, -0.0006, 0.0, 3669.8, 167],
                [24.0, 3.27, -0.006, 34.23, -0.0006, 0.0, 3690.2, 167],
                [24.0, 3.27, -0.006, 34.23, -0.0006, 0.0, 3690.2, 167],
                [24.0, 3.27, -0.006, 34.23, -0.0006, 0.0, 3690.2, 167],
                [24.0, 3.27, -0.006, 34.23, -0.0006, 0.0, 3690.2, 167],
            ]
        )
        manuel_veri = manuel_veri.reshape(1, 10, 8)
        tahmin = SOH_model.predict(manuel_veri)
        return {"predicted_soh": float(tahmin[0][0])}


@api_router.get("/api/data/{battery_id}")
def get_battery_data(battery_id: str, request: Request):
    with trace_endpoint(request, "get-battery-data"):
        filename = str(battery_folder / f"B00{battery_id}_discharge.csv")
        if not os.path.exists(filename):
            raise HTTPException(status_code=404, detail="Dosya bulunamadı")
        df = pd.read_csv(filename)
        df = df.sort_values(by="time")
        return df.to_dict(orient="records")
