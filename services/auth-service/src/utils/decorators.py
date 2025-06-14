import asyncio
import logging
import random
from functools import wraps
from typing import Any, AsyncGenerator, Callable, Coroutine, Type

from fastapi import HTTPException, status
from redis.asyncio import ConnectionError, RedisError, TimeoutError
from sqlalchemy.exc import (
    DBAPIError,
    DisconnectionError,
    IntegrityError,
    InterfaceError,
    MultipleResultsFound,
    NoResultFound,
    OperationalError,
)
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
            last_exception = None
            session = kwargs.get("session")

            if not session and len(args) >= 2:
                session = args[1]

            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exception as error:
                    await session.rollback()
                    last_exception = error
                    logger.error(
                        f"Возникло исключение: {error}. Попытка {attempt}/{max_attempts}",
                    )
                except Exception as error:
                    await session.rollback()
                    last_exception = error
                    logger.error(
                        f"Возникло исключение: {error}. Попытка {attempt}/{max_attempts}",
                    )

                if attempt == max_attempts:
                    logger.error("Backoff исчерпал попытки, прокидываю исключение...")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
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


def sqlalchemy_handler_400_exeptions[**P, R](
    func: Callable[P, Coroutine[Any, Any, R]],
) -> Callable[P, Coroutine[Any, Any, R | None]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        session = kwargs.get("session")
        if not session and len(args) >= 2:
            session = args[1]

        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Нарушение целостности данных: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нарушение уникальности",
            )

        except NoResultFound as e:
            await session.rollback()
            logger.warning(f"Запись не найдена: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Запись не найдена",
            )

        except MultipleResultsFound as e:
            await session.rollback()
            logger.error(f"Найдено несколько записей: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка: найдено несколько записей",
            )

    return wrapper


def sqlalchemy_universal_decorator[**P, R](
    func: Callable[P, Coroutine[Any, Any, R]],
) -> Callable[P, Coroutine[Any, Any, R | None]]:
    @backoff(
        exception=(DBAPIError, DisconnectionError, InterfaceError, OperationalError),
        max_attempts=5,
    )
    @sqlalchemy_handler_400_exeptions
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
