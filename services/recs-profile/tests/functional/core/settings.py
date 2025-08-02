from dotenv import find_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from tests.functional.core.logger_conf import get_logger

logger = get_logger(__name__)
ENV_FILE = find_dotenv()


class Postgres(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    db: str = "pg_db"

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class ContentAPI(BaseModel):
    host: str = "localhost"
    port: int = 8099
    rating_path: str = "/content-api/api/v1/films-rating/{film_id}"
    bookmark_path: str = "/content-api/api/v1/bookmarks/{film_id}"
    example_film: str = "b2faef9b-ad43-455c-9ea5-9d5977c84b73"

    @property
    def get_rating_url(self) -> str:
        return f"http://{self.host}:{self.port}{self.rating_path}".format(film_id=self.example_film)

    @property
    def get_bookmark_url(self) -> str:
        return f"http://{self.host}:{self.port}{self.bookmark_path}".format(
            film_id=self.example_film
        )


class AuthAPI(BaseModel):
    host: str = "localhost"
    port: int = 8001

    register_path: str = "/auth/api/v1/sessions/register"
    login_path: str = "/auth/api/v1/sessions/login"

    @property
    def host_service(self):
        return f"http://{self.host}:{self.port}"


class RecsAPI(BaseModel):
    host: str = "localhost"
    port: int = 8005
    path: str = "/recs-profile/api/v1/recs/fetch-user-recs"

    @property
    def get_url(self) -> str:
        return f"http://{self.host}:{self.port}{self.path}"


class TestConfig(BaseSettings):
    contentapi: ContentAPI = Field(default_factory=ContentAPI)
    authapi: AuthAPI = Field(default_factory=AuthAPI)
    postgres: Postgres = Postgres()
    recs_api: RecsAPI = RecsAPI()

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
