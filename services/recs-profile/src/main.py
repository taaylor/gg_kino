from api.v1.recs_profile import recs_api
from core.config import app_config
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from tracer_utils import init_tracer, request_id_middleware
from utils.connectors import lifespan
from utils.exceptions_handlers import setup_exception_handlers

app = FastAPI(
    title="API Профиля рекомендаций",
    version="1.0.0",
    description="Сервис управляет рекомендательным профилем пользователя",
    docs_url=app_config.docs_url,
    openapi_url=app_config.openapi_url,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# Подключение обработчиков
setup_exception_handlers(app)

if app_config.tracing:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    app.middleware("http")(request_id_middleware)
    # Инициализация трейсера
    init_tracer(app, app_config.project_name)
    FastAPIInstrumentor.instrument_app(app)

SERVICE_PATH = "/recs-profile/api/v1/"
app.include_router(recs_api.router, prefix=f"{SERVICE_PATH}recs", tags=["Рекомендации"])
