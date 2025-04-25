from api.v1.role import role
from core.config import app_config
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from utils.connectors import lifespan
from utils.exceptions_handlers import setup_exception_handlers

app = FastAPI(
    title="Auth API для онлайн-кинотеатра",
    version="1.0.0",
    docs_url=app_config.docs_url,
    openapi_url=app_config.openapi_url,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# Подключение обработчиков
setup_exception_handlers(app)

# app.include_router(example_root.router, prefix="/api/v1/example-root", tags=["example"])
app.include_router(role.router, prefix="/api/v1/role", tags=["role"])
