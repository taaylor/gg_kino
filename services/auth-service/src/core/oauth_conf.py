import logging

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Yandex(BaseSettings):
    client_id: str
    client_secret: str
    response_type: str = "code"
    scope: str = "login:info login:email"
    authorize_url: str = "https://oauth.yandex.ru/authorize"
    access_token_url: str = "https://oauth.yandex.ru/token"
    api_base_url: str = "https://login.yandex.ru/info"

    model_config = SettingsConfigDict(
        env_prefix="YANDEX_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


class ProvidersConf(BaseModel):
    yandex: Yandex = Yandex()


def get_providers_conf() -> ProvidersConf:
    conf = ProvidersConf()
    logger.info(f"Инициализация настроек провайдеров: {conf.model_dump_json()}")

    return conf


providers_conf = get_providers_conf()
