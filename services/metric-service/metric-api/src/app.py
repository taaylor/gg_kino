import atexit

from api.v1.api import metric_bp
from apiflask import APIFlask
from core.config import app_config
from utils.kafka_connector import shutdown_broker
from utils.rate_limiter import limiter

app = APIFlask(
    app_config.project_name,
    spec_path=app_config.openapi_url,
    docs_path=app_config.docs_url,
)

# Привязываю лимитер к приложению
limiter.init_app(app)


app.security_schemes = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Опциональное указание токена авторизации",
    },
}


app.register_blueprint(metric_bp, url_prefix="/metrics/v1")

atexit.register(shutdown_broker)
