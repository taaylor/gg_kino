import logging
from abc import ABC, abstractmethod
from typing import Coroutine

from redis.asyncio import Redis
from utils.decorators import redis_handler_exceptions

logger = logging.getLogger(__name__)


cache_conn: Redis | None = None


class Cache(ABC):
    """Абстрактный класс для работы с кэшем."""

    @abstractmethod
    def get(self, key: str) -> Coroutine[None, None, str | None]:
        """Получает значение из кэша по ключу."""

    @abstractmethod
    def destroy(self, key: str) -> Coroutine[None, None, None]:
        """Удаляет значение из кэша по ключу."""

    @abstractmethod
    def set(
        self, key: str, value: str, expire: int | None
    ) -> Coroutine[None, None, None]:  # noqa: WPS221
        """Сохраняет значение в кэш."""


class RedisCache(Cache):
    def __init__(self, redis: Redis):
        self.redis = redis

    @redis_handler_exceptions
    async def get(self, key: str) -> str | None:
        """Получает кеш из redis"""
        return await self.redis.get(key)

    @redis_handler_exceptions
    async def destroy(self, key: str):
        await self.redis.delete(key)
        logger.info(f"[RedisCache] Объект удален по ключу '{key}'")

    @redis_handler_exceptions
    async def set(self, key: str, value: str, expire: int | None):
        """Сохраняет кеш в redis"""
        await self.redis.set(key, value, ex=expire)
        logger.info(f"[RedisCache] Объект сохранён в кэш по ключу '{key}'")


async def get_cache() -> Cache:
    if cache_conn is None:
        raise ValueError("Cache не инициализирован")
    return RedisCache(cache_conn)
