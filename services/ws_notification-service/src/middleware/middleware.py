import logging

import jwt
from aiohttp import web
from core.config import app_config

logger = logging.getLogger(__name__)


async def authorize_middleware(app: web.Application, handler):  # noqa: WPS238, WPS231
    async def middleware_handler(request: web.Request):  # noqa: WPS231, WPS238, WPS430
        try:  # noqa: WPS229
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                raise web.HTTPUnauthorized(
                    reason="Требуется заголовок Authorization с Bearer токеном"
                )
            token = auth_header.split(" ")[1]
            decoded_token = jwt.decode(
                token,
                app_config.auth_public_key,
                algorithms=["RS256"],
            )
            key_session = app_config.redis.key_cache_drop_session.format(
                user_id=decoded_token.get("user_id"),
                session_id=decoded_token.get("session_id"),
            )

            if await app.get("cache_manager").get(key_session):
                raise web.HTTPUnauthorized(reason="Сессия пользователя неактивна")

            request.setdefault("user", decoded_token)
            logger.debug(f"Успешная авторизация пользователя {decoded_token.get("user_id")}")
            return await handler(request)

        except jwt.ExpiredSignatureError:
            raise web.HTTPUnauthorized(reason="Токен истек")

        except jwt.InvalidTokenError:
            raise web.HTTPUnauthorized(reason="Недействительный токен")

    return middleware_handler
