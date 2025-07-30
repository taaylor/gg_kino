import logging

import dotenv
from core.logger_config import LoggerSettings
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = dotenv.find_dotenv()

logger = logging.getLogger(__name__)


class Server(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    timeout: int = 30
    backlog: int = 512
    max_requests: int = 1000
    max_requests_jitter: int = 50
    worker_class: str = "gevent"


class Kafka(BaseModel):
    host1: str = "localhost"
    port1: int = 9094
    host2: str = "localhost"
    port2: int = 9095
    host3: str = "localhost"
    port3: int = 9096

    acks: int | str = 1  # 0, 1, 'all'
    retries: int = 3
    retry_backoff_ms: int = 100
    request_timeout_ms: int = 5000
    batch_size: int = 16384  # 16KB
    linger_ms: int = 5  # Ждать до 5ms для батчинга
    buffer_memory: int = 33554432  # 32MB

    security_protocol: str = "PLAINTEXT"  # PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL

    @property
    def get_servers(self) -> list[str]:
        return [
            f"{self.host1}:{self.port1}",
            f"{self.host2}:{self.port2}",
            f"{self.host3}:{self.port3}",
        ]

    like_topic: str = "user_metric_like_event"
    comment_topic: str = "user_metric_comment_event"
    watch_progress_topic: str = "user_metric_watch_progress_event"
    watch_list_topic: str = "user_metric_add_to_watch_list_event"
    other_topic: str = "user_metric_other_event"


class AppConfig(BaseSettings):
    project_name: str = "metric-api"
    docs_url: str = "/metrics/openapi"
    openapi_url: str = "/metrics/openapi.json"

    server: Server = Server()
    kafka: Kafka = Kafka()

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=False,
        env_nested_delimiter="_",
        extra="ignore",
    )


def _get_config() -> AppConfig:
    log = LoggerSettings()
    log.apply()

    app_config = AppConfig()
    logger.info(f"app_config.initialized: {app_config.model_dump_json(indent=4)}")
    return app_config


app_config = _get_config()
