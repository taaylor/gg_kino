import asyncio
import logging
from abc import ABC, abstractmethod
from functools import lru_cache
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

    @abstractmethod
    def background_set(
        self, key: str, value: str, expire: int | None
    ) -> Coroutine[None, None, None]:
        """Сохраняет значение в кэш в фоновом режиме."""

    @abstractmethod
    def background_destroy(self, *key: str) -> Coroutine[None, None, None]:
        """Удаляет значение из кэша в фоновом режиме."""

    @abstractmethod
    def scan_keys(
        self, pattern: str, count: int | None = None
    ) -> Coroutine[None, None, list[str]]:  # noqa: WPS211
        """
        Сканирует ключи, соответствующие заданному шаблону.

        :param pattern: Шаблон для поиска ключей.
        :param count: Максимальное количество ключей для возврата.
            Если None, возвращаются все ключи.
        :return: Список ключей, до 'count', если указано.
        """

    @abstractmethod
    def mget(self, keys: list[str]) -> Coroutine[None, None, list[str]]:
        """
        Отдает список объектов, хранящихся в виде JSON-значений по ключам.
        :param keys: список из одного или нескольких ключей.
        """


class RedisCache(Cache):  # noqa: WPS214
    """Реализация кэша на основе Redis."""

    __slots__ = ("redis",)

    def __init__(self, redis: Redis):
        self.redis = redis

    @redis_handler_exceptions
    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    @redis_handler_exceptions
    async def destroy(self, *key: str) -> None:
        await self.redis.delete(*key)
        logger.info(f"[RedisCache] Объект удален по ключу '{key}'")

    @redis_handler_exceptions
    async def set(self, key: str, value: str, expire: int | None):
        await self.redis.set(key, value, ex=expire)
        logger.info(f"[RedisCache] Объект сохранён в кэш по ключу '{key}'")

    @redis_handler_exceptions
    async def scan_keys(self, pattern: str, count: int | None = None) -> list[str]:  # type: ignore
        keys = []
        cursor = 0
        scan_count = 100

        while True:
            cursor, partial_keys = await self.redis.scan(
                cursor=cursor, match=pattern, count=scan_count
            )
            keys.extend(partial_keys)

            if count is not None and len(keys) >= count:
                break

            if cursor == 0:
                break

        if count is None:
            return keys
        return keys[:count]

    @redis_handler_exceptions
    async def mget(self, keys: list[str]) -> list[str]:  # type: ignore

        if not keys:
            return []

        result = await self.redis.mget(*keys)
        return [item for item in result if item]

    async def background_set(self, key: str, value: str, expire: int | None):
        asyncio.create_task(self.set(key=key, value=value, expire=expire))
        logger.debug(f"Объект будет сохранен в кеш по {key=}")

    async def background_destroy(self, *key: str) -> None:
        asyncio.create_task(self.destroy(*key))
        logger.debug(f"Объект будет удален в кеше по {key=}")


@lru_cache()
def get_cache() -> Cache:
    if cache_conn is None:
        raise ValueError("Соединение с кэшем не инициализировано")
    return RedisCache(redis=cache_conn)
