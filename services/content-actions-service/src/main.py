from api.v1.bookmark import bookmark_api
from api.v1.rating import rating_api
from api.v1.review import review_api
from core.config import app_config
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from utils.connectors import lifespan
from utils.exceptions_handlers import setup_exception_handlers

app = FastAPI(
    title="Content-actions API для онлайн-кинотеатра",
    version="1.0.0",
    description="Сервис пользовательских действий с контентом",
    docs_url=app_config.docs_url,
    openapi_url=app_config.openapi_url,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# Подключение обработчиков
setup_exception_handlers(app)

SERVICE_PATH = "/content-api/api/v1/"
app.include_router(rating_api.router, prefix=f"{SERVICE_PATH}films-rating", tags=["Рейтинг"])
app.include_router(review_api.router, prefix=f"{SERVICE_PATH}reviews", tags=["Рецензии"])
app.include_router(bookmark_api.router, prefix=f"{SERVICE_PATH}bookmarks", tags=["Закладки"])
