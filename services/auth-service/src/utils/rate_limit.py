import datetime
import logging
from functools import wraps
from typing import Any, Callable, Coroutine

from context import current_request
from db.cache import get_cache
from fastapi import HTTPException, status
from utils.decoders import decode_jwt_payload

logger = logging.getLogger(__name__)


async def get_identifier() -> str:
    """
    Определяет идентификатор пользователя: user_id из JWT или IP-адрес.
    """
    request = current_request.get()
    # Проверяем JWT
    if request.headers.get("authorization"):
        jwt_token = request.headers.get("authorization", "").split(" ")[-1]
        payload = decode_jwt_payload(jwt_token)
        if user_id := payload.get("user_id"):
            return f"user_id:{user_id}"

    # Если нет JWT, используем IP
    ip = request.headers.get(
        # в заголовке X-Forwarded-For nginx передаёт ip клиента (он включён)
        "X-Forwarded-For",
        # нужен на тот случай, если убрать X-Forwarded-For из nginx
        request.client.host,
    )  # .split(",")[0].strip()
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
            result = await pipe.execute()
            if result is None:  # Обработка ошибок от @redis_handler_exeptions
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
