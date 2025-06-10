from contextlib import asynccontextmanager

from beanie import init_beanie
from core.config import app_config
from db import cache
from fastapi import FastAPI
from models.models import LikeCollection
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):

    mongo_db = AsyncIOMotorClient("mongodb://user:pass@host:27017")
    await init_beanie(database=mongo_db.db_name, document_models=[LikeCollection])

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

    yield

    await cache.cache_conn.close()
    mongo_db.close()
