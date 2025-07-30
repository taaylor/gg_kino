from functools import wraps
from typing import Any, Callable, Coroutine

from core.logger_config import get_logger
from elasticsearch import BadRequestError as EsBadRequestError
from elasticsearch import NotFoundError as EsNotFoundError
from redis.asyncio import ConnectionError, RedisError, TimeoutError

logger = get_logger(__name__)


def redis_handler_exceptions[**P, R](
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
                f"[RedisCache] Неизвестная ошибка при работе с ключом: {error}",
            )

    return wrapper


def elastic_handler_exeptions[**P, R](
    func: Callable[P, Coroutine[Any, Any, R]],
) -> Callable[P, Coroutine[Any, Any, R | None]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return await func(*args, **kwargs)
        except EsBadRequestError as error:
            logger.error(
                f"[Elasticsearch] общая ошибка запроса \
                    (например, неверный формат запроса): {error}",
            )
            raise ValueError("Некорректный запрос") from error

        except EsNotFoundError as error:
            logger.error(f"Объект не найден: {error}")
            return None

    return wrapper
