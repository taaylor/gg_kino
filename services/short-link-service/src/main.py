from api.v1.link import link_api, link_redirect
from core.config import app_config
from fastapi import FastAPI, responses
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from tracer_utils import init_tracer, request_id_middleware
from utils.connectors import lifespan
from utils.exceptions_handlers import setup_exception_handlers

app = FastAPI(
    title="Link API для онлайн-кинотеатра",
    version="1.0.0",
    description="Сервис сокращения ссылок киносервиса",
    docs_url=app_config.docs_url,
    openapi_url=app_config.openapi_url,
    default_response_class=responses.ORJSONResponse,
    lifespan=lifespan,
)

setup_exception_handlers(app)

if app_config.tracing:
    app.middleware("http")(request_id_middleware)
    init_tracer(app, app_config.project_name)
    FastAPIInstrumentor.instrument_app(app)

SERVICE_PATH = "/link/api/v1"
app.include_router(link_api.router, prefix=f"{SERVICE_PATH}/link", tags=["Сокращение ссылки"])
app.include_router(link_redirect.router, prefix="/l", tags=["Роут по сокращённой ссылке"])
