from api.v1.nlp import nlp_api
from core.config import app_config
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from rate_limite_utils import RequestContextMiddleware
from tracer_utils import init_tracer, request_id_middleware
from utils.connectors import lifespan
from utils.exceptions_handlers import setup_exception_handlers

app = FastAPI(
    title="API Сервиса запроса персональной рекомендации",
    version="1.0.0",
    description="""Сервис принимает запрос пользователя на естественном
                    языке и находит рекомендованные фильмы""",
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
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    # Добавляем middleware
    app.middleware("http")(request_id_middleware)
    # Инициализация трейсера
    init_tracer(app, app_config.project_name)
    # Добавлене инструментария FastAPI для трейсов
    FastAPIInstrumentor.instrument_app(app)

SERVICE_PATH = "/nl/api/v1/"
app.include_router(nlp_api.router, prefix=f"{SERVICE_PATH}recs", tags=["Рекомендации"])
