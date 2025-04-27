from contextlib import asynccontextmanager

from core.config import app_config
from db import cache, elastic
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from redis.asyncio import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    elastic.es = AsyncElasticsearch(app_config.elastic.get_es_host(), request_timeout=20)
    yield

    await cache.cache_conn.close()
    await elastic.es.close()
