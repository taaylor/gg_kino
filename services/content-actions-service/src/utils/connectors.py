from contextlib import asynccontextmanager

# from beanie import init_beanie
from core.config import app_config
from db import cache
from fastapi import FastAPI
from redis.asyncio import Redis

"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

@asynccontextmanager
async def lifespan(_: FastAPI):
    client = AsyncIOMotorClient('mongodb://user:pass@host:27017')
    await init_beanie(database=client.db_name, document_models=[Post])
    yield
    client.close()

"""


@asynccontextmanager
async def lifespan(app: FastAPI):

    # engine = create_async_engine(app_config.postgres.ASYNC_DATABASE_URL, echo=True, future=True)
    # postgres.async_session_maker = sessionmaker(
    #     bind=engine,
    #     class_=AsyncSession,
    #     expire_on_commit=False,
    # )

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
    # await engine.dispose()
