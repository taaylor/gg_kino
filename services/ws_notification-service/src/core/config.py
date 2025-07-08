from dotenv import find_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Server(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    timeout: int = 30
    backlog: int = 512
    max_requests: int = 1000
    max_requests_jitter: int = 50
    worker_class: str = "aiohttp.GunicornWebWorker"


class RabbitMQ(BaseModel):
    hosts: list[str] = ["rabbitmq-1", "rabbitmq-3", "rabbitmq-3"]
    user: str = "user"
    password: str = "pass"
    review_like_queue: str = "user-review.liked.notification.websocket-sender"


class Redis(BaseModel):
    host: str = "localhost"
    port: int = 6379
    user: str = "redis_user"
    password: str = "Parol123"
    db: int = 0
    cache_expire_time: int = 360

    key_cache_drop_session: str = Field(
        default="session:drop:{user_id}:{session_id}",
        description="ключ по которому храняться отозванные сессии пользователя",
    )
    key_cache_send_event: str = Field(
        default="send_event:{user_id}:{event_id}",
        description="ключ по которому храняться отправленные нотификации пользователя",
    )
    key_cache_not_send_event: str = Field(
        default="not_send_event:{user_id}:{event_id}",
        description="ключ по которому храняться не отправленные обогащенные нотификации",
    )
    key_cache_fail_event: str = Field(
        default="fail_event:{user_id}:{event_id}",
        description="ключ по которому храняться не отправленные нотификации",
    )


class NotificationAPI(BaseModel):
    host: str = "localhost"
    port: int = 8000
    callback_path: str = "/notification/api/v1/notifications/update-sending-status"

    @property
    def get_url(self):
        return f"http://{self.host}:{self.port}{self.callback_path}"


class Config(BaseSettings):
    api_keys: list[str]
    rabbitmq: RabbitMQ = RabbitMQ()
    redis: Redis = Redis()
    server: Server = Server()
    notification_api: NotificationAPI = NotificationAPI()

    auth_public_key: str = """
    -----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArW7XpysaZje95xChyW8u
    L8xGDbvUezcygQNcYep97eM9Vurhk+5BSgNF5sQfW/IeMCH2EtbQi+tVuyTYcelG
    Gs2Flln/AHXdE6UqiS3AKvRxuvZTWetf80AGcyl7Sax2SY+j6sPSwy/q+SpaxYMf
    QOx0buewylTZ7MUkkepsDf7ZbYZfzyUOUUzGilDWeKskKNt9ujCdZYNy6+37xWru
    LsIdrTFC1/ggReddwEM4/VNvK5q+go+SCDfVgfQ8LbMiCgkKyZ3fgeP+KFsbCL/d
    iaqd0feQZY8tFMEttcBzQaZUny2pjJ+cBNmkRJG54vD1wl3ujSIfimJ2gQTmCPvf
    iwIDAQAB
    -----END PUBLIC KEY-----
    """

    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="_",
        extra="ignore",
    )


def get_config() -> Config:
    import logging

    from core.logger_conf import LoggerSettings

    logger_settings = LoggerSettings()
    logger_settings.apply()
    logger = logging.getLogger(__name__)

    config = Config()
    logger.debug(f"Инициализация конфигурации: {config.model_dump_json(indent=4)}")
    return config


app_config = get_config()
