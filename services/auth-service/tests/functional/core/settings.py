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


class RedisConf(BaseModel):
    host: str = "localhost"
    port: int = 6379
    user: str = "redis_user"
    password: str = "Parol123"
    db: int = 0


class AuthAPICong(BaseModel):
    host: str = "localhost"
    port: int = 8000

    @property
    def host_service(self):
        return f"http://{self.host}:{self.port}/auth/api/v1"


class TestConfig(BaseSettings):
    api_key: str = "9333954892f3ce159e33c829af5ea4b93cc2385306b45158ca95bc31f195c943"

    redis: RedisConf = Field(
        default_factory=RedisConf,
        description="Конфигурация Redis",
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
    logger.debug("конфигурация тестов auth-api:" + test_conf.model_dump_json())
    return test_conf


test_conf = _get_test_config()
