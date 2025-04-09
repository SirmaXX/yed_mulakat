from fastapi import FastAPI, Request
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
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


@app.get("/")
async def read_root():
    return {"message": "Hello World"}


@app.get("/test")
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
