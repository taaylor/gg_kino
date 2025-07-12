import asyncio
import logging
from abc import ABC, abstractmethod

from core.config import app_config
from redis.asyncio import Redis
from utils.decorators import redis_handler_exceptions

logger = logging.getLogger(__name__)


class Cache(ABC):
    @abstractmethod
    async def get(self, key: str) -> str | None:
        pass

    @abstractmethod
    async def destroy(self, key: str) -> None:
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire: int | None):
        pass

    @abstractmethod
    async def background_set(self, key: str, value: str, expire: int | None):
        pass

    @abstractmethod
    async def background_destroy(self, key: str) -> None:
        pass


class RedisCache(Cache):
    def __init__(self, redis: Redis):
        self.redis = redis

    @redis_handler_exceptions
    async def get(self, key: str) -> str | None:
        """Получает кеш из redis"""
        return await self.redis.get(key)

    @redis_handler_exceptions
    async def destroy(self, key: str) -> None:
        await self.redis.delete(key)
        logger.info(f"[RedisCache] Объект удален по ключу '{key}'")

    @redis_handler_exceptions
    async def set(self, key: str, value: str, expire: int | None):
        """Сохраняет кеш в redis"""
        await self.destroy(key)  # инвалидация кеша
        await self.redis.set(key, value, ex=expire)
        logger.info(f"[RedisCache] Объект сохранён в кэш по ключу '{key}'")

    async def background_set(self, key: str, value: str, expire: int | None):
        """Сохраняет кеш в фоновом процессе"""
        asyncio.create_task(self.set(key=key, value=value, expire=expire))
        logger.debug(f"Объект будет сохранен в кеш по {key=}")

    async def background_destroy(self, key: str) -> None:
        asyncio.create_task(self.destroy(key=key))
        logger.debug(f"Объект будет удален в кеше по {key=}")


cache_conn = Redis(
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


def get_cache() -> Cache:
    return RedisCache(cache_conn)
