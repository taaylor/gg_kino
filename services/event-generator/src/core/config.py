import logging

import dotenv
from celery.schedules import crontab
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
    worker_class: str = "uvicorn.workers.UvicornWorker"


class Redis(BaseModel):
    host: str = "localhost"
    port: int = 6379
    user: str = "redis_user"
    password: str = "Parol123"
    db: int = 0


class FilmApi(BaseModel):
    host: str = "localhost"
    port: int = 8001
    profile_path: str = "/async/api/v1/films/"

    @property
    def get_last_films_url(self) -> str:
        return f"http://{self.host}:{self.port}{self.profile_path}"


class NotificationAPI(BaseModel):
    host: str = "localhost"
    port: int = 8001
    profile_path: str = "/notification/api/v1/notifications/mass-notification"

    @property
    def send_to_mass_notification_url(self) -> str:
        return f"http://{self.host}:{self.port}{self.profile_path}"


class Postgres(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    db: str = "pg_db"

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"  # noqa: WPS221, E501


class RabbitMQ(BaseModel):
    host1: str = "localhost"
    host2: str = "localhost"
    host3: str = "localhost"
    port: int = 5672

    user: str = "user"
    password: str = "pass"

    @property
    def get_host(self) -> str:
        # broker=f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@rabbitmq-1:5672//",
        return f"amqp://{self.user}:{self.password}@{self.host1}:{self.port}//"


class AppConfig(BaseSettings):
    glitchtip_url: str = "url"
    is_glitchtip_enabled: bool = False
    project_name: str = "event-generator"
    docs_url: str = "/event-generator/openapi"
    openapi_url: str = "/event-generator/openapi.json"
    tracing: bool = False  # включение/выключение трассировки
    cache_expire_in_seconds: int = 300  # время кэширование ответа (сек.)
    default_http_timeout: float = 3.0

    celery_intervals: dict = {
        "test_reminder_get_fresh_films_10_seconds": 40,  # каждые 40 сек.
        "reminder_get_fresh_films_each_friday": crontab(
            minute=0, hour=9, day_of_week="fri"
        ),  # каждую неделю в пятницу утром
    }
    templates: dict = {"fresh_films": "104c743c-030c-41f9-a714-62392a46e71d"}

    postgres: Postgres = Postgres()
    rabbitmq: RabbitMQ = RabbitMQ()
    redis: Redis = Redis()
    server: Server = Server()
    filmapi: FilmApi = FilmApi()
    notification_api: NotificationAPI = NotificationAPI()

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
    logger.info(
        "app_config.initialized:"
        f"{app_config.model_dump_json(exclude={"celery_intervals"}, indent=4)}"
    )
    return app_config


app_config = _get_config()
