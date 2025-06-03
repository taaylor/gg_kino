import logging

import dotenv
from pydantic_settings import BaseSettings

ENV_FILE = dotenv.find_dotenv()

logger = logging.getLogger(__name__)


class KafkaConfig(BaseSettings):
    host_1: str = "kafka-0"
    host_2: str = "kafka-1"
    host_3: str = "kafka-2"
    port_1: int = 9092
    port_2: int = 9092
    port_3: int = 9092
    batch_size: int = 5000
    timeout_ms: int = 1000
    group_id: str = "metrics-etl-group"
    like_topic: str = "user_metric_like_event"  # LIKE_TOPIC
    comment_topic: str = "user_metric_comment_event"  # COMMENT_TOPIC
    watch_progress_topic: str = "user_metric_watch_progress_event"  # WATCH_PROGRESS_TOPIC
    watch_list_topic: str = "user_metric_add_to_watch_list_event"  # WATCH_LIST_TOPIC
    other_topic: str = "user_metric_other_event"  # OTHER_TOPIC

    @property
    def topics(self):
        return [
            self.like_topic,
            self.comment_topic,
            self.watch_progress_topic,
            self.watch_list_topic,
            self.other_topic,
        ]

    @property
    def bootstrap_servers(self):
        return [
            f"{self.host_1}:{self.port_1}",
            f"{self.host_2}:{self.port_2}",
            f"{self.host_3}:{self.port_3}",
        ]

    class Config:
        env_prefix = "KAFKA_"


class ClickHouseConfig(BaseSettings):
    # host: str = "localhost"
    host: str = "clickhouse-node1"
    port: int = 9000
    database: str = "kinoservice"
    table_name_dist: str = "metrics_dst"
    user: str = "default"  # Значение по умолчанию
    default_password: str = "1234"

    class Config:
        env_prefix = "CLK_"


kafka_config = KafkaConfig()
clickhouse_config = ClickHouseConfig()
