# import dotenv
# from core.logger_config import get_logger
# from pydantic_settings import BaseSettings

# ENV_FILE = dotenv.find_dotenv()

# logger = get_logger(__name__)


# class KafkaConfig(BaseSettings):
#     host_1: str = "kafka-0"
#     host_2: str = "kafka-1"
#     host_3: str = "kafka-2"
#     port_1: int = 9092
#     port_2: int = 9092
#     port_3: int = 9092
#     batch_size: int = 5000
#     timeout_ms: int = 1000
#     group_id: str = "metrics-etl-group"
#     like_topic: str = "user_metric_like_event"
#     comment_topic: str = "user_metric_comment_event"
#     watch_progress_topic: str = "user_metric_watch_progress_event"
#     watch_list_topic: str = "user_metric_add_to_watch_list_event"
#     other_topic: str = "user_metric_other_event"

#     @property
#     def topics(self):
#         return [
#             self.like_topic,
#             self.comment_topic,
#             self.watch_progress_topic,
#             self.watch_list_topic,
#             self.other_topic,
#         ]

#     @property
#     def bootstrap_servers(self):
#         return [
#             f"{self.host_1}:{self.port_1}",
#             f"{self.host_2}:{self.port_2}",
#             f"{self.host_3}:{self.port_3}",
#         ]

#     class Config:
#         env_prefix = "KAFKA_"


# class ClickHouseConfig(BaseSettings):
#     host: str = "clickhouse-node1"
#     port: int = 9000
#     database: str = "kinoservice"
#     table_name_dist: str = "metrics_dst"
#     user: str = "default"
#     default_password: str = "1234"

#     class Config:
#         env_prefix = "CLICKHOUSE_"


# def _get_kafka_config():
#     kafka_config = KafkaConfig()
#     logger.info(f"Конфигурация Kafka: {kafka_config.model_dump_json()}")
#     return kafka_config


# def _get_clickhouse_config():
#     clickhouse_config = ClickHouseConfig()
#     logger.info(f"Конфигурация ClickHouse: {clickhouse_config.model_dump_json()}")
#     return clickhouse_config


# clickhouse_config = _get_clickhouse_config()
# kafka_config = _get_kafka_config()

# ! -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
import logging
import os

import dotenv
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


class AppConfig(BaseSettings):
    project_name: str = "embedding-etl"
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_expire_in_seconds: int = 300
    embedding_dims: int = 768

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
    logger.info(f"app_config.initialized: {app_config.model_dump_json(indent=4)}")
    return app_config


app_config = _get_config()
# ! -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
