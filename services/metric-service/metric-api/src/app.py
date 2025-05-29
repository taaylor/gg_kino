from api.v1.api import metric_bp
from apiflask import APIFlask
from core.config import app_config

app = APIFlask(app_config.project_name)

app.register_blueprint(metric_bp)
