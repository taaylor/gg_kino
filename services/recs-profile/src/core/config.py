import logging

import dotenv
from core.logger_config import LoggerSettings
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = dotenv.find_dotenv()


class Server(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    timeout: int = 30
    backlog: int = 512
    max_requests: int = 1000
    max_requests_jitter: int = 50
    worker_class: str = "uvicorn.workers.UvicornWorker"


class Postgres(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    db: str = "pg_db"

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"  # noqa: WPS221, E501


class FilmApi(BaseModel):
    host: str = "localhost"
    port: int = 8008
    films_path: str = "/async/api/v1/internal/fetch-films"

    @property
    def get_film_url(self) -> str:
        return f"http://{self.host}:{self.port}{self.films_path}"


class EmbeddingAPI(BaseModel):
    host: str = "localhost"
    port: int = 8007
    path: str = "/embedding-service/api/v1/embedding/fetch-embeddings"

    @property
    def get_url(self) -> str:
        return f"http://{self.host}:{self.port}{self.path}"


class Kafka(BaseModel):
    host1: str = "localhost"
    port1: int = 9094
    host2: str = "localhost"
    port2: int = 9095
    host3: str = "localhost"
    port3: int = 9096

    retry_backoff_ms: int = 100
    request_timeout_ms: int = 10000
    batch_size: int = 5120
    linger_ms: int = 5
    buffer_memory: int = 33554432
    security_protocol: str = "PLAINTEXT"

    @property
    def get_servers(self) -> list[str]:
        return [
            f"{self.host1}:{self.port1}",
            f"{self.host2}:{self.port2}",
            f"{self.host3}:{self.port3}",
        ]

    rec_bookmarks_list_topic: str = "user_content_add_film_to_bookmarks_event"
    rec_user_ratings_films_topic: str = "user_content_users_ratings_films_event"


class AppConfig(BaseSettings):
    tracing: bool = False
    project_name: str = "recs-profile"
    docs_url: str = "/recs-profile/openapi"
    openapi_url: str = "/recs-profile/openapi.json"
    expire_cache_sec: int = 3600
    high_rating_score: int = 7
    template_film_embedding: str = "{title}. {genres}. {description} {rating_text}"

    server: Server = Server()
    postgres: Postgres = Postgres()
    filmapi: FilmApi = FilmApi()
    embedding_api: EmbeddingAPI = EmbeddingAPI()
    kafka: Kafka = Kafka()

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=False,
        env_nested_delimiter="_",
        extra="ignore",
    )


def _get_config() -> AppConfig:
    log = LoggerSettings()
    log.apply()
    logger = logging.getLogger(__name__)
    app_config = AppConfig()
    logger.info(f"app_config.initialized: {app_config.model_dump_json(indent=4)}")
    return app_config


app_config = _get_config()
