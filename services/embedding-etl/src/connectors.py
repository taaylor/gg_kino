from contextlib import asynccontextmanager

from core.config import app_config
from db import cache, elastic
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis


@asynccontextmanager
async def lifespan():
    cache.cache_conn = Redis(
        host="localhost",
        # host=app_config.redis.host,
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
    elastic.es = AsyncElasticsearch(
        # app_config.elastic.get_es_host(),
        "http://localhost:9200",
        request_timeout=20,
    )
    yield
    await cache.cache_conn.close()
    await elastic.es.close()
