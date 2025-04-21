from core.config import app_config
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from api.v1 import example_root

app = FastAPI(
    title="Auth API для онлайн-кинотеатра",
    version="1.0.0",
    docs_url=app_config.docs_url,
    openapi_url=app_config.openapi_url,
    default_response_class=ORJSONResponse,
)
app.include_router(example_root.router, prefix="/api/v1/example-root", tags=["example"])