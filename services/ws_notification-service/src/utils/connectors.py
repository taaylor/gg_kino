from typing import AsyncIterator

from aiohttp import web
from core.config import app_config
from db import cache
from redis.asyncio import Redis


async def lifespan(app: web.Application) -> AsyncIterator[None]:

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
    app["cache"] = cache.get_cache()

    yield

    await cache.cache_conn.close()
