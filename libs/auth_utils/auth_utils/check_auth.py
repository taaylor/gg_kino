import logging

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import Request, Response
from pydantic import BaseModel
from redis.asyncio import Redis

from .auth_utils_config import auth_utils_conf

logger = logging.getLogger(__name__)

CACHE_KEY_DROP_SESSION = auth_utils_conf.cache_key_drop_session

redis_conn = Redis(
    host=auth_utils_conf.redis.host,
    port=auth_utils_conf.redis.port,
    username=auth_utils_conf.redis.user,
    password=auth_utils_conf.redis.password,
    db=auth_utils_conf.redis.db,
)


# Кастомный класс, чтобы не было конфликтов с обычным AuthJWT
class LibAuthJWT(AuthJWT):
    """Изолированная версия AuthJWT для библиотеки"""

    pass


# Кастомный класс, чтобы не было конфликтов с обычным AuthJWT
class LibAuthJWTBearer(AuthJWTBearer):
    """Bearer с изолированной конфигурацией"""

    def __call__(self, req: Request = None, res: Response = None) -> LibAuthJWT:
        return LibAuthJWT(req=req, res=res)  # Возвращаем экземпляр кастомного класса


class JWTSettings(BaseModel):
    authjwt_algorithm: str = auth_utils_conf.algorithm
    authjwt_public_key: str = auth_utils_conf.public_key
    authjwt_denylist_enabled: bool = auth_utils_conf.denylist_enabled
    authjwt_denylist_token_checks: set = auth_utils_conf.token_checks


@LibAuthJWT.load_config
def get_config():
    settings = JWTSettings()
    logger.info(f"Конфигурация JWT библиотеки: {settings.model_dump_json()}")
    return settings


@AuthJWT.token_in_denylist_loader
async def check_if_session_in_denylist(decrypted_token: dict) -> bool:
    logger.info(f"Проверка токена: {decrypted_token}")
    user_id = decrypted_token.get("user_id")
    session_id = decrypted_token.get("session_id")

    cache_key = CACHE_KEY_DROP_SESSION.format(user_id=user_id, session_id=session_id)
    entry = await redis_conn.get(cache_key)
    return entry is not None


auth_dep = LibAuthJWTBearer()
