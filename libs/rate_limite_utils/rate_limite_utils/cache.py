import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine

from redis.asyncio import Redis, RedisError
from redis.asyncio.client import Pipeline
from .rate_limite_utils_config import rate_limite_utils_conf

logger = logging.getLogger(__name__)


cache_conn = Redis(
    host=rate_limite_utils_conf.host,
    port=rate_limite_utils_conf.port,
    db=rate_limite_utils_conf.db,
    decode_responses=True,
    username=rate_limite_utils_conf.user,
    password=rate_limite_utils_conf.password,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_error=False,
    retry_on_timeout=False,
)


def redis_handler_exeptions[**P, R](
    func: Callable[P, Coroutine[Any, Any, R]],
) -> Callable[P, Coroutine[Any, Any, R | None]]:
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return await func(*args, **kwargs)
        except ConnectionError as error:
            logger.error(f"[RedisCache] Ошибка соединения: {error}")
        except TimeoutError as error:
            logger.error(f"[RedisCache] Timeout соединения: {error}")
        except RedisError as error:
            logger.error(
                f"[RedisCache] Неизвестная ошибка при работе с ключом: {error}")

    return wrapper


class Cache(ABC):

    @abstractmethod
    def pipeline(self):
        pass

    @abstractmethod
    async def pipeline_execute(self, pipe: Pipeline) -> list:
        pass

    @abstractmethod
    async def lrange(self, key: str, start: int, end: int) -> list[bytes]:
        pass


class RedisCache(Cache):
    def __init__(self, redis: Redis):
        self.redis = redis

    def pipeline(self):
        """Создаёт Redis pipeline для атомарных операций."""
        return self.redis.pipeline()

    @redis_handler_exeptions
    async def pipeline_execute(self, pipe: Pipeline) -> list | None:
        """Выполняет команды в pipeline и возвращает результаты."""
        result = await pipe.execute()
        logger.info(
            (
                "[RedisCache] Pipeline выполнился с "
                f"{len(result) if result else None} результатом."
            )
        )
        return result

    @redis_handler_exeptions
    async def lrange(self, key: str, start: int, end: int) -> list[bytes]:
        """Извлекает список из Redis по ключу в диапазоне."""
        return await self.redis.lrange(key, start, end)


async def get_cache() -> Cache:
    if cache_conn is None:
        raise ValueError("Cache не инициализирован")
    return RedisCache(cache_conn)
