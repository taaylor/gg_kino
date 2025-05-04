import asyncio
import logging
import random
from functools import wraps
from http import HTTPStatus
from typing import Any, AsyncGenerator, Callable, Coroutine, Type

from fastapi import HTTPException
from redis.asyncio import ConnectionError, RedisError, TimeoutError
from sqlalchemy.exc import DBAPIError, DisconnectionError, InterfaceError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

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


def backoff(
    exception: tuple[Type[Exception], ...] = (
        OperationalError,
        DisconnectionError,
        DBAPIError,
        InterfaceError,
    ),
    start_sleep_time: float = 0.1,
    factor: float = 2,
    border_sleep_time: float = 10,
    jitter: bool = True,
    max_attempts: int = 5,
):

    def func_wrapper[**P, R](
        func: Callable[P, Coroutine[Any, Any, R]],
    ) -> Callable[P, Coroutine[Any, Any, R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> AsyncGenerator[AsyncSession, None]:
            time = start_sleep_time
            attempt = 1
            last_exception = None

            while attempt <= max_attempts:
                try:
                    async for session in func(*args, **kwargs):
                        yield session
                    return
                except exception as error:
                    last_exception = error
                    logger.error(f"Возникло исключение: {error}. Попытка {attempt}/{max_attempts}")
                except HTTPException:
                    raise
                except Exception as error:
                    last_exception = error
                    logger.error(f"Возникло исключение: {error}. Попытка {attempt}/{max_attempts}")
                if attempt == max_attempts:
                    logger.error("Backoff исчерпал попытки, прокидываю исключение...")
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_GATEWAY,
                        detail="Ошибка стороннего сервиса, повторите попытку позже",
                    ) from last_exception

                if jitter:
                    time += random.uniform(0, time * 0.1)
                await asyncio.sleep(time)
                time = min(time * factor, border_sleep_time)
                attempt += 1

            raise RuntimeError("Неожиданная ошибка в backoff")

        return wrapper

    return func_wrapper
