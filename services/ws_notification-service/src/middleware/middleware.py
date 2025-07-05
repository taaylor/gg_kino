import jwt
from aiohttp import web
from core.config import app_config


async def authorize_middleware(request: web.Request, handler):
    async def middleware_handler(request: web.Request):
        try:
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
            key_session = app_config.cache_key_drop_session.format(
                user_id=decoded_token.get("user_id"),
                session_id=decoded_token.get("session_id"),
            )
            session = await request.get("cache").get(key_session)

            if session:
                raise web.HTTPUnauthorized(reason="Сессия пользователя неактивна")

            request.setdefault("user", decoded_token)
            return await handler(request)
        except jwt.ExpiredSignatureError:
            raise web.HTTPUnauthorized(reason="Токен истек")
        except jwt.InvalidTokenError:
            raise web.HTTPUnauthorized(reason="Недействительный токен")

    return middleware_handler
