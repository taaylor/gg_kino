import logging

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from core.config import app_config
from models.logic_models import SessionUserData
from pydantic import BaseModel

logger = logging.getLogger(__name__)

auth_dep = AuthJWTBearer()


def load_jwt_settings():
    try:
        with open(app_config.jwt.private_key_path, encoding="utf-8") as private_key_file:
            private_key = private_key_file.read()
        with open(app_config.jwt.public_key_path, encoding="utf-8") as public_key_file:
            public_key = public_key_file.read()
    except FileNotFoundError as e:
        raise ValueError(f"Не удалось найти файл ключа: {e}")
    except Exception as e:
        raise ValueError(f"Ошибка при чтении ключей: {e}")

    return JWTSettings(authjwt_public_key=public_key, authjwt_private_key=private_key)


class JWTSettings(BaseModel):
    authjwt_algorithm: str = app_config.jwt.algorithm
    authjwt_public_key: str
    authjwt_private_key: str
    authjwt_access_token_expires: int = app_config.jwt.access_token_lifetime_sec
    authjwt_refresh_token_expires: int = app_config.jwt.refresh_token_lifetime_sec


class JWTProcessor:
    def __init__(self):
        # Используем оригинальный AuthJWT
        self.authorize = AuthJWT()

    async def create_tokens(self, user_data: SessionUserData):
        access_token = await self.authorize.create_access_token(
            subject=str(user_data.session_id),
            user_claims=user_data.model_dump(mode="json"),
        )
        refresh_token = await self.authorize.create_refresh_token(
            subject=str(user_data.session_id),
            user_claims=user_data.model_dump(mode="json"),
        )
        return access_token, refresh_token


@AuthJWT.load_config  # Конфигурация для оригинального AuthJWT
def get_config():
    return load_jwt_settings()


async def get_key_manager():
    return JWTProcessor()
