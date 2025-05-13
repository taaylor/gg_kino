import logging

import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = dotenv.find_dotenv()

logger = logging.getLogger(__name__)

logger.info(f"ENV RATE LIMITE: {ENV_FILE}")


class RedisConfig(BaseSettings):
    host: str = "localhost"
    port: int = 6379
    user: str = "redis_user"
    password: str = "Parol123"
    db: int = 0

    model_config = SettingsConfigDict(
        env_prefix="Redis_",
        env_file=ENV_FILE,
        case_sensitive=False,
        env_nested_delimiter="_",
        extra="ignore",
    )


def _get_config() -> RedisConfig:
    app_config = RedisConfig()
    logger.info(f"rate_limite_utils_conf.initialized: {app_config.model_dump_json(indent=4)}")
    return app_config


rate_limite_utils_conf = _get_config()
