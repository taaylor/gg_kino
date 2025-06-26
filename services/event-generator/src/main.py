import logging

from core.config import app_config
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from rate_limite_utils import RequestContextMiddleware
from tracer_utils import init_tracer, request_id_middleware
from utils.connectors import lifespan
from utils.exceptions_handlers import setup_exception_handlers

logger = logging.getLogger(__name__)

# Инициализация Sentry/GlitchTip ПЕРЕД созданием приложения
if app_config.is_glitchtip_enabled:
    logger.info("GlitchTip Включен")

    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_sdk.init(
        dsn=app_config.glitchtip_url,
        integrations=[
            StarletteIntegration(),
            FastApiIntegration(),
        ],
        traces_sample_rate=1.0,  # Отслеживает 100% транзакций
        environment="development",
    )

app = FastAPI(
    title="Content-actions API для онлайн-кинотеатра",
    version="1.0.0",
    description="Сервис пользовательских действий с контентом",
    docs_url=app_config.docs_url,
    openapi_url=app_config.openapi_url,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

if app_config.tracing:
    logger.info("Трейсер Включен")
    # Добавляем middleware
    app.middleware("http")(request_id_middleware)
    # Инициализация трейсера
    init_tracer(app, app_config.project_name)
    # Добавлене инструментария FastAPI для трейсов
    FastAPIInstrumentor.instrument_app(app)

# Подключение обработчиков
setup_exception_handlers(app)


# Добавляю миддлвар для доступа Request во всех эндпоинтах
app.add_middleware(RequestContextMiddleware)

SERVICE_PATH = "/content-api/api/v1/"
app.include_router(rating_api.router, prefix=f"{SERVICE_PATH}films-rating", tags=["Рейтинг"])
app.include_router(review_api.router, prefix=f"{SERVICE_PATH}reviews", tags=["Рецензии"])
app.include_router(bookmark_api.router, prefix=f"{SERVICE_PATH}bookmarks", tags=["Закладки"])
app.include_router(
    private_api.router, prefix=f"{SERVICE_PATH}private", tags=["API для тестирования утилит"]
)
