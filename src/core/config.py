import logging
import os

import dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# from src.core.logger_config import LoggerSettings
from core.logger_config import LoggerSettings

# Применяем настройки логирования
ENV_FILE = dotenv.find_dotenv()

logger = logging.getLogger(__name__)


class Server(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    timeout: int = 30
    backlog: int = 512
    max_requests: int = 1000
    max_requests_jitter: int = 50
    worker_class: str = "uvicorn.workers.UvicornWorker"

class Postgres(BaseSettings):
    host: str = 'postgres'
    # host: str = 'localhost'
    port: int = 5432
    user: str = 'postgres'
    password: str = 'postgres'
    # db_name: str = 'postgres'
    db_name: str = 'pg_db'

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


class Redis(BaseModel):
    host: str = "localhost"
    port: int = 6379
    user: str = "redis_user"
    password: str = "Parol123"
    db: int = 0


class AppConfig(BaseSettings):
    project_name: str = "movies"
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_url: str = "/api/openapi"
    openapi_url: str = "/api/openapi.json"
    cache_expire_in_seconds: int = 300  # время кэширование ответа (сек.)

    db: Postgres = Postgres()
    redis: Redis = Redis()
    server: Server = Server()

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_prefix="api_",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )


def _get_config() -> AppConfig:
    # установка настроек для логов
    log = LoggerSettings()
    log.apply()

    app_config = AppConfig()
    logger.info(f"app_config.initialized: {app_config.model_dump_json()}")
    return app_config


app_config = _get_config()
