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
        self.timeout = app_config.rec_profile_supplier.timeout

    async def fetch_rec_profile_user(self, user_id: UUID) -> list[list[float]] | None:
        url = app_config.rec_profile_supplier.get_url
        user_id_str = str(user_id)
        body = {
            "user_ids": [
                user_id_str,
            ]
        }
        rec_profile = await self._make_request(HTTPMethod.POST, url, body)
        if rec_profile:
            rec_profile_dto = self._parser_embeddings(rec_profile.get("recs", {}))
            return rec_profile_dto.get(user_id_str)
        return None

    @backoff.on_exception(
        backoff.expo,
        (httpx.RequestError, httpx.HTTPStatusError),
        max_tries=3,
        jitter=backoff.full_jitter,
    )
    @handle_http_errors(service_name="recs-profile")
    async def _make_request(
        self, method: HTTPMethod, url: str, data: dict | None = None
    ) -> dict[str, Any] | None:

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
            return response_data

    @staticmethod
    def _parser_embeddings(rec_profiles: list[dict[str, Any]]) -> dict[str, list[list[float]]]:
        embeddings = {}
        validate_func = lambda x: isinstance(x, float)  # noqa: E731

        for user in rec_profiles:
            user_id = user.get("user_id")
            for embedding in user.get("embeddings", []):
                emb = embedding.get("embedding", [])

                if (
                    emb
                    and len(emb) == app_config.embedding_dims
                    and all(validate_func(e) for e in emb)
                ):
                    if user_id not in embedding:
                        embeddings[user_id] = []
                    embeddings[user_id].append(emb)

        logger.info(f"Получены вектора для {len(embeddings)} пользователей")
        return embeddings


@lru_cache
def get_rec_profile_supplier() -> RecProfileSupplier:
    return RecProfileSupplier()
