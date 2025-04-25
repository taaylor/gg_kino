from api.v1.auth import auth_api
from api.v1.update_user_data.routers import router
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

app.include_router(router, prefix="/api/v1/users", tags=["users"])
app.include_router(auth_api.router, tags=["auth"])
