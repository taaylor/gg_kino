from api.v1.bookmark import bookmark_api
from api.v1.like import like_api
from api.v1.review import review_api
from core.config import app_config
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from rate_limite_utils import RequestContextMiddleware
from tracer_utils import init_tracer, request_id_middleware
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

# Добавляю миддлвар для доступа Request во всех эндпоинтах
app.add_middleware(RequestContextMiddleware)

if app_config.tracing:
    # Добавляем middleware
    app.middleware("http")(request_id_middleware)
    # Инициализация трейсера
    init_tracer(app, app_config.project_name)
    # Добавлене инструментария FastAPI для трейсов
    FastAPIInstrumentor.instrument_app(app)

SERVICE_PATH = "/content-actions/api/v1/"
app.include_router(like_api.router, prefix=f"{SERVICE_PATH}likes", tags=["Лайки"])
app.include_router(review_api.router, prefix=f"{SERVICE_PATH}reviews", tags=["Рецензии"])
app.include_router(bookmark_api.router, prefix=f"{SERVICE_PATH}bookmarks", tags=["Закладки"])
