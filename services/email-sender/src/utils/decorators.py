import asyncio
import logging
import random
from functools import wraps
from typing import Any, AsyncGenerator, Callable, Coroutine, Type

from redis.asyncio import ConnectionError, RedisError, TimeoutError
from sqlalchemy.exc import (  # IntegrityError,; MultipleResultsFound,; NoResultFound,
    DBAPIError,
    DisconnectionError,
    InterfaceError,
    OperationalError,
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


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


def backoff(
    exception: tuple[Type[Exception], ...],
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
        async def wrapper(
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> AsyncGenerator[AsyncSession, None]:
            time = start_sleep_time
            attempt = 1
            # last_exception = None
            session = kwargs.get("session")

            if not session and len(args) >= 2:
                session = args[1]

            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exception as error:
                    await session.rollback()
                    # last_exception = error
                    logger.error(
                        f"Возникло исключение: {error}. Попытка {attempt}/{max_attempts}",
                    )
                except Exception as error:
                    await session.rollback()
                    # last_exception = error
                    logger.error(
                        f"Возникло исключение: {error}. Попытка {attempt}/{max_attempts}",
                    )

                if attempt == max_attempts:
                    logger.error("Backoff исчерпал попытки, прокидываю исключение...")
                    raise ValueError
                    # raise HTTPException(
                    #     status_code=status.HTTP_502_BAD_GATEWAY,
                    #     detail="Ошибка стороннего сервиса, повторите попытку позже",
                    # ) from last_exception

                if jitter:
                    time += random.uniform(0, time * 0.1)
                await asyncio.sleep(time)
                time = min(time * factor, border_sleep_time)
                attempt += 1

            raise RuntimeError("Неожиданная ошибка в backoff")

        return wrapper

    return func_wrapper


def sqlalchemy_universal_decorator[**P, R](
    func: Callable[P, Coroutine[Any, Any, R]],
) -> Callable[P, Coroutine[Any, Any, R | None]]:
    @backoff(
        exception=(DBAPIError, DisconnectionError, InterfaceError, OperationalError),
        max_attempts=5,
    )
    @wraps(func)
    async def wrapper(*args, **kwargs):
        session = kwargs.get("session")
        if not session and len(args) >= 2:
            session = args[1]

        if session is None:
            raise ValueError("Сессия должна быть передана в функцию")

        result = await func(*args, **kwargs)
        await session.commit()
        return result

    return wrapper
