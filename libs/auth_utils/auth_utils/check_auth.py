import logging

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from pydantic import BaseModel
from redis import Redis


from .auth_utils_config import auth_utils_conf


logger = logging.getLogger(__name__)


redis_conn = Redis(
    host=auth_utils_conf.redis.host,
    port=auth_utils_conf.redis.port,
    username=auth_utils_conf.redis.user,
    password=auth_utils_conf.redis.password,
    db=auth_utils_conf.redis.db,
)


class LibAuthJWT(AuthJWT):
    """Изолированная версия AuthJWT для библиотеки"""

    pass


class LibAuthJWTBearer(AuthJWTBearer):
    """Bearer с изолированной конфигурацией"""

    pass


class JWTSettings(BaseModel):
    authjwt_algorithm = auth_utils_conf.algorithm
    authjwt_public_key = auth_utils_conf.public_key
    authjwt_denylist_enabled = auth_utils_conf.denylist_enabled
    authjwt_denylist_token_checks = auth_utils_conf.authjwt_denylist_token_checks


@LibAuthJWT.load_config
def get_config():
    return JWTSettings()


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token) -> bool:
    jti = decrypted_token["jti"]
    entry = redis_conn.get(jti)
    return entry and entry == "true"


auth_dep = LibAuthJWTBearer()
