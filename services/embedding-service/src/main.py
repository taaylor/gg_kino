from api.v1 import embedding_api
from core.config import app_config
from fastapi import FastAPI, responses
from utils.exceptions_handlers import setup_exception_handlers
from utils.lifespan import lifespan

app = FastAPI(
    debug=app_config.debug,
    version="1.0.0",
    title="Embedding API для получения вектора",
    description="Сервис для получения вектора",
    docs_url=app_config.docs_url,
    openapi_url=app_config.openapi_url,
    default_response_class=responses.ORJSONResponse,
    lifespan=lifespan,
)

setup_exception_handlers(app)

SERVICE_PATH = "/embedding-service/api/v1/"
app.include_router(
    embedding_api.router, prefix=f"{SERVICE_PATH}embedding", tags=["Получение вектора"]
)
