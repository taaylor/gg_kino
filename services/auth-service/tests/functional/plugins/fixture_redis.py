import json
from typing import Any

import pytest_asyncio
from redis.asyncio import Redis
from tests.functional.core.config_log import get_logger
from tests.functional.core.settings import test_conf

logger = get_logger(__name__)


@pytest_asyncio.fixture(name="redis_client", scope="session")
async def redis_client():
    redis_client = Redis(
        host=test_conf.redis.host,
        port=test_conf.redis.port,
        username=test_conf.redis.user,
        password=test_conf.redis.password,
        db=test_conf.redis.db,
    )
    yield redis_client
    await redis_client.close()


@pytest_asyncio.fixture(name="redis_test")
async def redis_test(redis_client: Redis):
    async def inner(key: str, cached_data: bool = True) -> list[dict[str, Any]] | None:
        """
        : cached_data: bool - праметр отвечает должен ли объекты находится в кеше по ключу

        """
        data = await redis_client.get(key)

        if cached_data:
            if not data:
                raise AssertionError(f"[REDIS] Ожидались данные в кеше, но {key=} пуст")

            logger.debug(f"[REDIS] Данные получены с кеша {key=}. Удаляю кеш...")
            response = json.loads(data)
            await redis_client.delete(key)

            if await redis_client.exists(key):
                raise AssertionError(f"[REDIS] Не удалось удалить кеш по ключу {key=}")
            logger.info("[REDIS] Кеш успешно удалён")
            return response
        else:
            if data:
                raise AssertionError(f"[REDIS] Не ожидалось наличие кеша, но {key=} заполнен")
            logger.debug(f"[REDIS] Кеш по ключу {key=} отсутствует, как и ожидалось")
            return None

    yield inner

    await redis_client.flushdb()
    logger.debug("[REDIS] База данных очищена")
