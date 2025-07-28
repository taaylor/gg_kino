import logging
from functools import lru_cache
from http import HTTPMethod
from typing import Any
from uuid import UUID

import backoff
import httpx
from core.config import app_config
from utils.http_decorators import handle_http_errors

logger = logging.getLogger(__name__)


class RecProfileSupplier:

    def __init__(self):
        self.timeout = 30

    async def fetch_rec_profile_user(self, user_id: UUID) -> list[list[float]]:
        # url = app_config.rec_profile_supplier.path_url
        # rec_profile = await self._make_request(HTTPMethod.POST, url, {"user_id": user_id})

        return [[1.0 for _ in range(384)], [1.0 for _ in range(384)]]

    @backoff.on_exception(
        backoff.expo,
        (httpx.RequestError, httpx.HTTPStatusError),
        max_tries=3,
        jitter=backoff.full_jitter,
    )
    @handle_http_errors(service_name="REC-service")
    async def _make_request(
        self, method: HTTPMethod, url: str, data: dict | None = None
    ) -> dict[str, Any]:

        async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
            host = app_config.rec_profile_supplier.host
            logger.debug(f"Сформирована строка запроса: {url}")

            match method:
                case HTTPMethod.POST:
                    response = await client.post(url=url, json=data)
                    response.raise_for_status()
                case _:
                    raise ValueError(f"Метод: {method} не поддерживается.")

            if not response.content:
                logger.error(f"Пустой ответ от сервиса {host}")

            response_data = response.json()
            logger.debug(
                f"Получен ответ от сервиса {host}: " f"{len(response_data)} векторов пользователя"
            )
            return response


@lru_cache
def get_rec_profile_supplier() -> RecProfileSupplier:
    return RecProfileSupplier()
