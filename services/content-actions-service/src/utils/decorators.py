import logging
from typing import Any, Callable, Coroutine

from redis.asyncio import ConnectionError, RedisError, TimeoutError

logger = logging.getLogger(__name__)


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
            logger.error(f"[RedisCache] Неизвестная ошибка при работе с ключом: {error}")

    return wrapper
