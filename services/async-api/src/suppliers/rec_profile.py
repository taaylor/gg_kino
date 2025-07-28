import logging
from functools import lru_cache
from http import HTTPMethod
from typing import Any
from uuid import UUID

import backoff
import httpx
from utils.http_decorators import handle_http_errors

logger = logging.getLogger(__name__)


class RecProfileSupplier:

    def __init__(self):
        self.timeout = 30

    async def fetch_rec_profile_user(self, user_id: UUID) -> list[list[float]]:
        return [[1.0 for _ in range(384)]]

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

        # TODO: пока так, ожидаем завершения сервиса rec-profiles
        async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
            client = client
            logger.debug(f"Сформирована строка запроса: {url}")

            match method:
                case _:
                    return []


@lru_cache
def get_rec_profile_supplier() -> RecProfileSupplier:
    return RecProfileSupplier()
