from dotenv import find_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .config_log import get_logger

logger = get_logger(__name__)

ENV_FILE = find_dotenv()


class ESConf(BaseModel):
    host: str = "localhost"
    port: int = 9200
    index_films: str = "movies"
    index_genres: str = "genres"
    index_persons: str = "persons"

    @property
    def es_host(self):
        return f"http://{self.host}:{self.port}"


class RedisConf(BaseModel):
    host: str = "localhost"
    port: int = 6379
    user: str = "redis_user"
    password: str = "Parol123"
    db: int = 0


class APIConf(BaseModel):
    host: str = "localhost"
    port: int = 8000

    @property
    def host_service(self):
        return f"http://{self.host}:{self.port}/api"


class TestConfig(BaseSettings):
    redis: RedisConf = Field(default_factory=RedisConf, description="Конфигурация Redis")
    elastic: ESConf = Field(default_factory=ESConf, description="Конфигурация ElasticSearch")
    asyncapi: APIConf = Field(
        default_factory=APIConf, description="Конфигурация сервиса AsyncAPI FastAPI"
    )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_prefix="test_",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )


def _get_test_config() -> TestConfig:
    test_conf = TestConfig()
    logger.debug(test_conf.model_dump_json())
    return test_conf


test_conf = _get_test_config()
