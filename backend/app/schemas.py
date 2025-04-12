from pydantic import BaseModel, Field
from datetime import date
from typing import List
from typing import Optional


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
