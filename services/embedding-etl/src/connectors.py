from contextlib import asynccontextmanager

from core.config import app_config
from core.logger_config import get_logger
from db import cache, elastic
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan():
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
    logger.info(f"Успешная инициализация Redis: {cache.cache_conn}")
    elastic.es = AsyncElasticsearch(
        app_config.elastic.get_es_host,
        request_timeout=20,
    )
    yield
    await cache.cache_conn.close()
    await elastic.es.close()
