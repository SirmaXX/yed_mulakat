from fastapi import APIRouter, Depends, Request, HTTPException, status
from tensorflow.keras.models import load_model
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pathlib import Path

import numpy as np

from app.schemas import PredictionRequest


# Dependency

soc_model_path = Path(__file__).parent / "SOC_LSTM.h5"
soh_model_path = Path(__file__).parent / "SOH_LSTM.h5"
# Modelleri yükle
SOC_model = load_model(soc_model_path)
SOH_model = load_model(soh_model_path)


api_router = APIRouter(responses={404: {"description": "Not found"}})


@api_router.get(
    "/health", description="servisin çalışıp çalışmadığını kontrol eden router"
)
async def health(req: Request):
    health = True
    if health == True:
        return True
    else:
        return None


@api_router.get("/", description="index için router")
async def api_index():
    return {"message": "Hello from FastAPI!"}


@api_router.get(
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
@api_router.get(
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


@api_router.get(
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


@api_router.get(
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
