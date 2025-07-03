from pydantic import BaseModel
from pydantic_settings import BaseSettings


class RabbitMQ(BaseModel):
    host: str = "localhost"
    user: str = "user"
    password: str = "pass"


class Redis(BaseModel):
    host: str = "localhost"
    port: int = 6379
    user: str = "redis_user"
    password: str = "Parol123"
    db: int = 0


class Config(BaseSettings):
    rabbitmq: RabbitMQ = RabbitMQ()
    redis: Redis = Redis()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_config() -> Config:
    from core.logger_conf import get_logger

    logger = get_logger(__name__)
    config = Config()
    logger.debug(f"Config loaded: {config.model_dump()}")
    return config


app_config = get_config()
