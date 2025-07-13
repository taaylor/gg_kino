import logging
import os

import dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = dotenv.find_dotenv()

logger = logging.getLogger(__name__)


class Postgres(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    db: str = "pg_db"

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @property
    def SYNC_DATABASE_URL(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class Redis(BaseModel):
    host: str = "localhost"
    port: int = 6379
    user: str = "redis_user"
    password: str = "Parol123"
    db: int = 0

    key_cache_send_event: str = Field(
        default="send_event:{user_id}:{event_id}",
        description="ключ по которому хранятся отправленные письма пользователю",
    )
    key_cache_not_send_event: str = Field(
        default="not_send_event:{user_id}:{event_id}",
        description="ключ по которому хранятся не отправленные обогащенные письма",
    )
    key_cache_fail_event: str = Field(
        default="fail_event:{user_id}:{event_id}",
        description="ключ по которому хранятся не отправленные письма",
    )


class RabbitMQ(BaseModel):
    hosts: list[str] = ["rabbitmq-1", "rabbitmq-3", "rabbitmq-3"]
    user: str = "user"
    password: str = "pass"
    registered_queue: str = "user.registered.notification.email-sender"
    manager_mailing_queue: str = "manager-mailing.launched.notification.email-sender"
    auto_mailing_queue: str = "auto-mailing.launched.notification.email-sender"

    @property
    def get_queue_list(self):
        return [
            self.registered_queue,
            self.manager_mailing_queue,
            self.auto_mailing_queue,
        ]


class SmtpConfig(BaseModel):
    email_yandex_kinoservice: str = "skipped_work@yandex.ru"
    smtp_host: str = "mailhog"
    smtp_port: int = 1025


class NotificationApi(BaseModel):
    host: str = "localhost"
    port: int = 8002
    profile_path: str = "/notification/api/v1/notifications/update-sending-status"

    @property
    def update_status_url(self) -> str:
        return f"http://{self.host}:{self.port}{self.profile_path}"


class AppConfig(BaseSettings):
    project_name: str = "email-sender"
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_expire_in_seconds: int = 300  # время кэширование ответа (сек.)
    cache_expire_in_seconds_for_email: int = 300 * 10 * 10  # время кэширование ответа (сек.)

    rabbitmq: RabbitMQ = RabbitMQ()
    postgres: Postgres = Postgres()
    redis: Redis = Redis()
    smtp: SmtpConfig = SmtpConfig()
    notification_api: NotificationApi = NotificationApi()

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=False,
        env_nested_delimiter="_",
        extra="ignore",
    )


def _get_config() -> AppConfig:

    app_config = AppConfig()
    logger.info(f"app_config.initialized: {app_config.model_dump_json(indent=4)}")
    return app_config


app_config = _get_config()
