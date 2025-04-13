from pydantic import BaseModel, Field
from datetime import date
from typing import List
from typing import Optional


# Modeller için veri yapıları
from pydantic import BaseModel
from typing import List


class SOHPredictInput(BaseModel):
    data: List[List[float]]  # 10x8 matris olacak
