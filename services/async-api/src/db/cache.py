import asyncio
import logging
from abc import ABC, abstractmethod

from redis.asyncio import Redis
from utils.decorators import redis_handler_exeptions

logger = logging.getLogger(__name__)

cache_conn: Redis | None = None


class Cache(ABC):
    @abstractmethod
    async def get(self, key: str) -> str | None:
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire: int | None):
        pass

    @abstractmethod
    async def background_set(self, key: str, value: str, expire: int | None):
        pass


class RedisCache(Cache):
    def __init__(self, redis: Redis):
        self.redis = redis

    @redis_handler_exeptions
    async def get(self, key: str) -> str | None:
        """Получает кеш из redis"""
        return await self.redis.get(key)

    @redis_handler_exeptions
    async def set(self, key: str, value: str, expire: int | None):
        """Сохраняет кеш в redis"""
        await self.redis.set(key, value, expire)
        logger.info(f"[RedisCache] Объект сохранён в кэш по ключу '{key}'")

    async def background_set(self, key: str, value: str, expire: int | None):
        """Сохраняет кеш в фоновом процессе"""
        asyncio.create_task(self.set(key=key, value=value, expire=expire))
        logger.debug(f"Объект будет сохранен в кеш по {key=}")


async def get_cache() -> Cache:
    if cache_conn is None:
        raise ValueError("Cache не инициализирован")
    return RedisCache(cache_conn)
