from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.routes import api_router


def create_app():
    app = FastAPI(title="Yed Teknoloji", description="Yed Teknoloji mülakat servisi")
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app)
    app.include_router(api_router)
    return app
