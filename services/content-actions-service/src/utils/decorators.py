import functools
import logging
from typing import Any, Callable, Coroutine

from beanie import exceptions as beanie_exp
from fastapi import HTTPException, status
from pymongo import errors as mongoerr
from redis.asyncio import ConnectionError, RedisError, TimeoutError

logger = logging.getLogger(__name__)


def redis_handler_exceptions[**P, R](
    func: Callable[P, Coroutine[Any, Any, R]],
) -> Callable[P, Coroutine[Any, Any, R | None]]:
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return await func(*args, **kwargs)
        except ConnectionError as error:
            logger.error(f"[RedisCache] Ошибка соединения: {error}")
            return None
        except TimeoutError as error:
            logger.error(f"[RedisCache] Timeout соединения: {error}")
            return None
        except RedisError as error:
            logger.error(f"[RedisCache] Неизвестная ошибка при работе с ключом: {error}")
            return None

    return wrapper


def mongodb_handler_exceptions[**P, R](  # noqa: WPS238, WPS231
    func: Callable[P, Coroutine[Any, Any, R]],
) -> Callable[P, Coroutine[Any, Any, R]]:
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:  # noqa: WPS238
        try:  # noqa: WPS225
            return await func(*args, **kwargs)
        except mongoerr.DuplicateKeyError as error:
            logger.warning(
                f"[MongoDB] Дублирование уникального ключа \
                    в {func.__name__}, {args=}, {kwargs=}: {error}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Документ с таким идентификатором уже существует",
            )
        except beanie_exp.DocumentNotFound as error:
            logger.warning(
                f"[MongoDB] Документ не найден \
                    в {func.__name__}, {args=}, {kwargs=}: {error}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Документ не найден"
            )
        except mongoerr.WriteError as error:
            logger.error(f"[MongoDB] Ошибка записи в {func.__name__}, {args=}, {kwargs=}: {error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Ошибка при записи данных"
            )
        except mongoerr.OperationFailure as error:
            logger.error(
                f"[MongoDB] Сбой операции с бд в {func.__name__}, \
                        {args=}, {kwargs=}: {error}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Сервис не доступен, повторите попытку позже",
            )

    return wrapper
