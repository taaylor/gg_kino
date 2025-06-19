# import sentry_sdk
from api.v1.bookmark import bookmark_api
from api.v1.rating import rating_api
from api.v1.review import review_api
from core.config import app_config
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from rate_limite_utils import RequestContextMiddleware

# from sentry_sdk.integrations.fastapi import FastApiIntegration
# from sentry_sdk.integrations.starlette import StarletteIntegration
from utils.connectors import lifespan
from utils.exceptions_handlers import setup_exception_handlers

# sentry_sdk.init(
#     dsn=app_config.glitchtip_url,
#     integrations=[
#         StarletteIntegration(),
#         FastApiIntegration(),
#     ],
#     traces_sample_rate=1.0,  # Отслеживает 100% транзакций
#     environment="development",
# )

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

# Добавляю миддлвар для доступа Request во всех эндпоинтах
app.add_middleware(RequestContextMiddleware)

SERVICE_PATH = "/content-api/api/v1/"
app.include_router(rating_api.router, prefix=f"{SERVICE_PATH}films-rating", tags=["Рейтинг"])
app.include_router(review_api.router, prefix=f"{SERVICE_PATH}reviews", tags=["Рецензии"])
app.include_router(bookmark_api.router, prefix=f"{SERVICE_PATH}bookmarks", tags=["Закладки"])


# @app.get("/content-api/api/v1/error")
# async def trigger_error():
#     """Тестовый эндпоинт для glitchtip"""
#     division_by_zero = 1 / 0  # noqa: F841, WPS344
#     return {"message": "Деление на 0"}
