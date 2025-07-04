from aiohttp import web
from core.config import app_config
from redis.asyncio import Redis
from storage import cache


async def setup_cache(app: web.Application):
    """
    Устанавливает соединение с хранилищем кеша при инициализации приложения
    """
    cache.cache_conn = Redis(
        host=app_config.redis.host,
        port=app_config.redis.port,
        db=app_config.redis.db,
        decode_responses=True,
        username=app_config.redis.user,
        password=app_config.redis.password,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_error=False,
        retry_on_timeout=False,
    )
    app.setdefault("cache_conn", cache.cache_conn)
    app.setdefault(
        "cache", cache.get_cache()
    )  # Позволяет сразу инициализировать экземпляр класса с кешем некий аналог Depends в FastAPI


async def cleanup_cache(app: web.Application):
    """
    Закрывает соединение с хранилищем кеша при инициализации приложения
    """
    if cache_conn := app.get("cache_conn"):
        await cache_conn.close()


async def setup_rabbitmq(app: web.Application):
    pass
