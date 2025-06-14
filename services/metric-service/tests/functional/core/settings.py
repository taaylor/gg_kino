from dotenv import find_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from tests.functional.core.logger_conf import get_logger

logger = get_logger(__name__)
ENV_FILE = find_dotenv()


class MetricsAPI(BaseModel):
    host: str = "localhost"
    port: int = 8000

    def get_url_api(self):
        return f"http://{self.host}:{self.port}/metrics/v1"


class ClickHouse(BaseModel):
    host: str = "localhost"
    port: int = 9000
    database: str = "kinoservice"
    table_name_dist: str = "metrics_dst"
    user: str = "default"
    default_password: str = "1234"


class TestConfig(BaseSettings):
    clickhouse: ClickHouse = Field(default_factory=ClickHouse)
    metricsapi: MetricsAPI = Field(default_factory=MetricsAPI)

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_prefix="test_",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )


def _get_test_config():
    test_conf = TestConfig()
    logger.info(f"Конфигурация тестов: {test_conf.model_dump_json()}")
    return test_conf


test_conf = _get_test_config()
