from dotenv import find_dotenv
from pydantic import BaseModel  # , Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .config_log import get_logger

logger = get_logger(__name__)

ENV_FILE = find_dotenv()


class EmbeddingApi(BaseModel):
    host: str = "localhost"
    port: str = 8007
    path_to_fetch_embedding: str = "/embedding-service/api/v1/embedding/fetch-embeddings"

    @property
    def url_for_embedding(self):
        return f"http://{self.host}:{self.port}{self.path_to_fetch_embedding}"


class TestConfig(BaseSettings):

    # embedding_api: EmbeddingApi = Field(
    #     default_factory=EmbeddingApi,
    #     description="Конфигурация сервиса Embedding",
    # )
    embedding_api: EmbeddingApi = EmbeddingApi()

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
