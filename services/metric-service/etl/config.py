import logging

import dotenv

# from pydantic import BaseModel
from pydantic_settings import BaseSettings  # , SettingsConfigDict

ENV_FILE = dotenv.find_dotenv()

logger = logging.getLogger(__name__)


class KafkaConfig(BaseSettings):
    host_0: str = "kafka-0"
    host_1: str = "kafka-1"
    host_2: str = "kafka-2"
    port: int = 9092

    @property
    def bootstrap_servers(self):
        return [
            f"{self.host_0}:{self.port}",
            f"{self.host_1}:{self.port}",
            f"{self.host_2}:{self.port}",
        ]


class ClickHouseConfig(BaseSettings):
    host: str = "localhost"
    port: int = 9000


kafka_config = KafkaConfig()
clickhouse_config = ClickHouseConfig()
