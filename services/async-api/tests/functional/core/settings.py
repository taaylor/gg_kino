from dotenv import find_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .config_log import get_logger

logger = get_logger(__name__)

ENV_FILE = find_dotenv()


class Postgres(BaseModel):
    host: str = "postgres"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    db: str = "pg_db"

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


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
        return f"http://{self.host}:{self.port}/async/api/v1"


class AuthAPICong(BaseModel):
    host: str = "localhost"
    port: int = 8000

    @property
    def host_service(self):
        return f"http://{self.host}:{self.port}/auth/api/v1"


class TestConfig(BaseSettings):
    redis: RedisConf = Field(
        default_factory=RedisConf,
        description="Конфигурация Redis",
    )
    elastic: ESConf = Field(
        default_factory=ESConf,
        description="Конфигурация ElasticSearch",
    )
    asyncapi: APIConf = Field(
        default_factory=APIConf,
        description="Конфигурация сервиса AsyncAPI FastAPI",
    )
    postgres: Postgres = Field(
        default_factory=Postgres,
        description="Конфигурация Postgres",
    )
    authapi: AuthAPICong = Field(
        default_factory=AuthAPICong,
        description="Конфигурация сервиса Auth",
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
