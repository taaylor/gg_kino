import logging

from api.v1 import notify_api, template_api
from core.config import app_config
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from tracer_utils import init_tracer, request_id_middleware
from utils.connectors import lifespan
from utils.exceptions_handlers import setup_exception_handlers

logger = logging.getLogger(__name__)

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
        traces_sample_rate=1.0,
        environment="development",
    )

app = FastAPI(
    title="Генератор событий для создания переодических уведомлений",
    version="1.0.0",
    description="Сервис генератора событий для уведомлений",
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
SERVICE_PATH = "/event-generator/api/v1/"
app.include_router(
    template_api.router, prefix=f"{SERVICE_PATH}admin", tags=["Управление шаблонами"]
)
app.include_router(notify_api.router, prefix=f"{SERVICE_PATH}notify", tags=["Создание рассылок"])
