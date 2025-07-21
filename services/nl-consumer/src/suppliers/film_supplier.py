import logging
from uuid import UUID

import httpx
from core.config import app_config
from models.logic_models import Film
from pydantic import TypeAdapter
from utils.http_decorators import EmptyServerResponse, handle_http_errors

logger = logging.getLogger(__name__)


class FilmSupplier:
    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout

    @handle_http_errors(service_name=app_config.profileapi.host)
    async def fetch_films(self, film_ids: set[UUID]) -> list[Film]:  # noqa: WPS210
        logger.info(f"Получение фильмов: {len(film_ids)} " f"от сервиса {app_config.filmapi.host}")

        async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
            data = {"film_ids": [str(film_id) for film_id in film_ids]}
            url = app_config.filmapi.get_film_url

            logger.debug(f"Сформирована строка запроса фильмов: {url}")
            logger.debug(f"Сформирована data запроса фильмов: {data}")

            response = await client.post(url=url, json=data)
            # Все HTTP ошибки обработает декоратор через raise_for_status()
            response.raise_for_status()

            # Проверяем наличие контента
            if not response.content:
                logger.error(
                    f"Пустой ответ от сервиса {app_config.filmapi.host} для фильмов {film_ids}"
                )
                raise EmptyServerResponse("Получен пустой ответ от сервиса фильмов")

            response_data = response.json()

            logger.debug(
                f"Получен ответ от сервиса {app_config.filmapi.host}: "
                f"{len(response_data)} фильмов"
            )

            adapter = TypeAdapter(list[Film])
            films = adapter.validate_python(response_data)

            logger.info(f"Фильмы: {len(films)} успешно получены")
            return films


def get_film_supplier() -> FilmSupplier:
    return FilmSupplier()
