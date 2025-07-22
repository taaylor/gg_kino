import logging
import os

import dotenv
from celery.schedules import crontab
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# Применяем настройки логирования
ENV_FILE = dotenv.find_dotenv()

logger = logging.getLogger(__name__)


class Elastic(BaseModel):
    host: str = "localhost"
    port: int = 9200

    def get_es_host(self) -> str:
        return f"http://{self.host}:{self.port}"


class Redis(BaseModel):
    host: str = "localhost"
    port: int = 6379
    user: str = "redis_user"
    password: str = "Parol123"
    db: int = 0
    db_for_qeueu: int = 1

    @property
    def get_redis_host(self):
        # redis://[<user>[:<password>]@]<host>[:<port>]/<db>
        return f"redis://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_for_qeueu}"


class AppConfig(BaseSettings):
    project_name: str = "embedding-etl"
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_expire_in_seconds: int = 300
    embedding_dims: int = 768
    celery_intervals: dict = {
        "test_reminder_get_data": 10,  # каждые 10 сек.
        "reminder_get_fresh_films_each_friday": crontab(
            minute=0, hour=9, day_of_week="fri"
        ),  # каждую неделю в пятницу утром
    }

    elastic: Elastic = Elastic()
    redis: Redis = Redis()

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=False,
        env_nested_delimiter="_",
        extra="ignore",
    )


def _get_config() -> AppConfig:

    app_config = AppConfig()
    logger.info(ENV_FILE)
    logger.info(
        "app_config.initialized:"
        f"{app_config.model_dump_json(exclude={"celery_intervals"}, indent=4)}"
    )
    return app_config


app_config = _get_config()
