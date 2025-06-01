import atexit

from api.v1.api import metric_bp
from apiflask import APIFlask
from core.config import app_config
from utils.kafka_connector import shutdown_broker

app = APIFlask(
    app_config.project_name, spec_path=app_config.openapi_url, docs_path=app_config.docs_url
)

app.register_blueprint(metric_bp)

atexit.register(shutdown_broker)
