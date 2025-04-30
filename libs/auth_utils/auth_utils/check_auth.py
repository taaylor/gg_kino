import logging
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LibAuthJWT(AuthJWT):
    """Изолированная версия AuthJWT для библиотеки"""

    pass


class LibAuthJWTBearer(AuthJWTBearer):
    """Bearer с изолированной конфигурацией"""
    pass


class JWTSettings(BaseModel):
    authjwt_algorithm: str = "RS256"
    authjwt_public_key: str
    authjwt_access_token_expires: int = 300
    authjwt_refresh_token_expires: int = 1200


def load_jwt_settings():
    public_key = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArW7XpysaZje95xChyW8u
L8xGDbvUezcygQNcYep97eM9Vurhk+5BSgNF5sQfW/IeMCH2EtbQi+tVuyTYcelG
Gs2Flln/AHXdE6UqiS3AKvRxuvZTWetf80AGcyl7Sax2SY+j6sPSwy/q+SpaxYMf
QOx0buewylTZ7MUkkepsDf7ZbYZfzyUOUUzGilDWeKskKNt9ujCdZYNy6+37xWru
LsIdrTFC1/ggReddwEM4/VNvK5q+go+SCDfVgfQ8LbMiCgkKyZ3fgeP+KFsbCL/d
iaqd0feQZY8tFMEttcBzQaZUny2pjJ+cBNmkRJG54vD1wl3ujSIfimJ2gQTmCPvf
iwIDAQAB
-----END PUBLIC KEY-----
"""
    return JWTSettings(authjwt_public_key=public_key)


@LibAuthJWT.load_config
def get_config():
    return load_jwt_settings()


auth_dep = LibAuthJWTBearer()
