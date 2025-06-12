from api.v1.bookmark import bookmark_api
from api.v1.like import like_api
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

SERVICE_PATH = "/content-actions/api/v1/"
app.include_router(like_api.router, prefix=f"{SERVICE_PATH}likes/films", tags=["Лайки"])
app.include_router(review_api.router, prefix=f"{SERVICE_PATH}reviews/films", tags=["Рецензии"])
app.include_router(bookmark_api.router, prefix=f"{SERVICE_PATH}bookmarks/films", tags=["Закладки"])

"""
SERVICE_PATH = "/content-actions/api/v1"
# Префикс для операций над фильмами:
films_prefix = f"{SERVICE_PATH}/films"

app.include_router(like_api.router, prefix=films_prefix, tags=["Лайки"])
app.include_router(bookmark_api.router, prefix=films_prefix, tags=["Закладки"])
app.include_router(review_api.router, prefix=films_prefix, tags=["Рецензии"])
"""
