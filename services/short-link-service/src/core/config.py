import logging

import dotenv
from core.logger_config import LoggerSettings
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = dotenv.find_dotenv()


class Server(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    timeout: int = 30
    backlog: int = 512
    max_requests: int = 1000
    max_requests_jitter: int = 50
    worker_class: str = "uvicorn.workers.UvicornWorker"


class ShortLink(BaseModel):
    protocol: str = "http"
    short_host: str = "localhost"
    short_port: str = ""  # Для локальной отладки можно указать порт ":8009"
    service_path: str = "l"
    link_lifetime_days: int = 10

    @property
    def get_short_url(self) -> str:
        return f"{self.protocol}://{self.short_host}{self.short_port}/{self.service_path}/"


class Postgres(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    db: str = "pg_db"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"  # noqa: WPS221, E501


class AppConfig(BaseSettings):
    tracing: bool = False
    project_name: str = "link-service"
    docs_url: str = "/link/openapi"
    openapi_url: str = "/link/openapi.json"

    server: Server = Server()
    postgres: Postgres = Postgres()
    shortlink: ShortLink = ShortLink()

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=False,
        env_nested_delimiter="_",
        extra="ignore",
    )


def _get_config() -> AppConfig:
    log = LoggerSettings()
    log.apply()
    logger = logging.getLogger(__name__)
    app_config = AppConfig()
    logger.info(f"app_config.initialized: {app_config.model_dump_json(indent=4)}")
    return app_config


app_config = _get_config()
