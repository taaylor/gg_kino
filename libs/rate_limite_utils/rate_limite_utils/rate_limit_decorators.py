import datetime
import logging
import time
from functools import wraps
from typing import Any, Callable, Coroutine

from auth_utils import auth_dep
from fastapi import HTTPException, status

from .cache import get_cache
from .context import current_request

logger = logging.getLogger(__name__)


async def get_identifier() -> str:
    """
    Определяет идентификатор пользователя: user_id из JWT или IP-адрес.
    """
    request = current_request.get()
    # Проверяем JWT
    if request.headers.get("authorization"):
        jwt_token = request.headers.get("authorization", "").split(" ")[-1]
        payload = await auth_dep().get_raw_jwt(jwt_token)
        logger.info(f"Key limiter - {payload}")
        if user_id := payload.get("user_id"):
            return f"user_id:{user_id}"

    # Если нет JWT, используем IP
    ip = request.headers.get(
        # в заголовке X-Forwarded-For nginx передаёт ip клиента (он включён)
        "X-Forwarded-For",
        # нужен на тот случай, если убрать X-Forwarded-For из nginx
        request.client.host,
    )
    return f"ip:{ip}"


def rate_limit(limit: int = 20, window: int = 60):
    """
    Декоратор для rate limiting с использованием Redis.
    limit: максимальное количество запросов.
    window: временное окно в секундах.
    """

    def func_wrapper[**P, R](
        func: Callable[P, Coroutine[Any, Any, R]],
    ) -> Callable[P, Coroutine[Any, Any, R]]:
        @wraps(func)
        async def wrapper(
            *args: P.args,
            **kwargs: P.kwargs,
        ):
            identifier = await get_identifier()
            cache = await get_cache()
            now = datetime.datetime.now()
            key = f"rate_limit:{identifier}:{now.minute}"

            # Используем pipeline для атомарности
            pipe = cache.pipeline()
            pipe.incr(key, 1)  # Увеличиваем счётчик запросов
            pipe.expire(key, window - 1)  # Устанавливаем время жизни ключа
            result = await cache.pipeline_execute(pipe)
            if result is None:
                logger.error(f"Redis pipeline упал по ключу: {key}")
                return await func(*args, **kwargs)
            request_number = result[0]  # Получаем текущее количество запросов

            if request_number > limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too Many Requests"
                )
            return await func(*args, **kwargs)

        return wrapper

    return func_wrapper


def rate_limit_leaky_bucket(
    bucket_size: int = 20, leak_rate: float = 0.333, time_to_live: int = 10 * 60
):  # 1 запрос каждые 3 секунды
    """
    Декоратор для rate limiting с использованием Leaky Bucket.
    bucket_size: Максимальное количество запросов в ведре.
    leak_rate: Скорость протекания (запросов в секунду).
    """

    def func_wrapper[**P, R](
        func: Callable[P, Coroutine[Any, Any, R]],
    ) -> Callable[P, Coroutine[Any, Any, R]]:
        @wraps(func)
        async def wrapper(
            *args: P.args,
            **kwargs: P.kwargs,
        ):
            identifier = await get_identifier()
            cache = await get_cache()
            now = time.time()  # Текущее время в секундах
            key = f"leaky_bucket:{identifier}"

            # Время, за которое "протекает" один запрос
            leak_interval = 1.0 / leak_rate

            # Получаем временные метки запросов из Redis
            requests = await cache.lrange(key, 0, -1)
            try:
                requests = [float(r) for r in requests] if requests else []
            except ValueError:
                requests = []
            # requests = [float(r) for r in requests] if requests else []

            # Удаляем "протёкшие" запросы
            while requests and (now - requests[0] > leak_interval):
                requests.pop(0)
            # Проверяем, прошло ли достаточно времени с последнего запроса
            if requests and (now - requests[-1] < leak_interval):
                raise HTTPException(
                    status_code=429, detail="Too Many Requests - wait before sending again"
                )
            # Проверяем, не переполнено ли ведро
            if len(requests) < bucket_size:
                # Используем pipeline для добавления запроса и установки TTL
                pipe = cache.pipeline()
                pipe.rpush(key, now)  # Добавляем новую временную метку
                pipe.expire(key, time_to_live)  # Устанавливаем TTL
                await cache.pipeline_execute(pipe)
            else:
                # Ведро переполнено
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too Many Requests"
                )

            return await func(*args, **kwargs)

        return wrapper

    return func_wrapper
