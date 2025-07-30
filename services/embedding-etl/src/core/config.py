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

    @property
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


class EmbeddingApi(BaseModel):
    host: str = "localhost"
    port: str = 8007
    path_to_fetch_embedding: str = "/embedding-service/api/v1/embedding/fetch-embeddings"

    @property
    def url_for_embedding(self):
        return f"http://{self.host}:{self.port}{self.path_to_fetch_embedding}"


class AppConfig(BaseSettings):
    project_name: str = "embedding-etl"
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index: str = "movies"
    cache_expire_in_seconds: int = 60 * 60  # 1 час
    time_start_etl_seconds: int = 60 * 5  # 5 минут
    embedding_dims: int = 384
    celery_intervals: dict = {
        "test_reminder_get_data": 10,  # каждые 10 сек.
        "reminder_get_fresh_films_each_friday": crontab(minute=0, hour=9, day_of_week="fri"),
    }
    template_embedding: str = "{title}. {genres}. {description} {rating_text}"
    run_start_key: str = "embedding-etl:unix-timestamp:run-start"
    last_run_key: str = "embedding-etl:unix-timestamp:last-run"
    batch_size_etl: int = 50

    high_rating_level: int = 7

    embedding_api: EmbeddingApi = EmbeddingApi()
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
