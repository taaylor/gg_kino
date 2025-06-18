from dotenv import find_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from tests.functional.core.logger_conf import get_logger

logger = get_logger(__name__)
ENV_FILE = find_dotenv()


class ContentAPI(BaseModel):
    host: str = "localhost"
    port: int = 8099

    @property
    def host_service(self):
        return f"http://{self.host}:{self.port}/content-api/api/v1"


class AuthAPI(BaseModel):
    host: str = "localhost"
    port: int = 8000

    register_path: str = "/auth/api/v1/sessions/register"
    login_path: str = "/auth/api/v1/sessions/login"

    @property
    def host_service(self):
        return f"http://{self.host}:{self.port}"


class Redis(BaseModel):
    host: str = "localhost"
    port: int = 6379
    user: str = "redis_user"
    password: str = "Parol123"
    db: int = 0


class MongoDB(BaseModel):
    host: str = "localhost"
    port: int = 27017
    name: str = "kinoservice"
    like_coll: str = "likeCollection"
    bookmark_coll: str = "bookmarkCollection"
    reviews_coll: str = "reviewsCollection"

    @property
    def ASYNC_DATABASE_URL(self):
        return f"mongodb://{self.host}:{self.port}"


class TestConfig(BaseSettings):
    mongodb: MongoDB = Field(default_factory=MongoDB)
    contentapi: ContentAPI = Field(default_factory=ContentAPI)
    redis: Redis = Field(default_factory=Redis)
    authapi: AuthAPI = Field(default_factory=AuthAPI)

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_prefix="test_",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )


def _get_test_config():
    test_conf = TestConfig()
    logger.info(f"Конфигурация тестов: {test_conf.model_dump_json(indent=4)}")
    return test_conf


test_conf = _get_test_config()
