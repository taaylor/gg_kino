import logging

import httpx
from core.config import app_config
from models.logic_models import FilmListResponse, GenreResponse
from pydantic import TypeAdapter
from utils.http_decorators import EmptyServerResponse, handle_http_errors

logger = logging.getLogger(__name__)


class FilmSupplier:
    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout

    @handle_http_errors(service_name=app_config.filmapi.host)
    async def fetch_genres(self) -> set[str]:
        url = app_config.filmapi.get_genre_url

        genres_json = await self._make_request("get", url)
        list_genres = await self._convert_to_model(genres_json, GenreResponse)
        logger.info(f"Получен список из: {len(list_genres)} жанров.")

        return {genre.name for genre in list_genres}  # type: ignore

    @handle_http_errors(service_name=app_config.filmapi.host)
    async def fetch_films(self, vector: list[float]) -> list[FilmListResponse]:
        url = app_config.filmapi.get_film_url
        data = {"vector": vector}

        films_json = await self._make_request("post", url, data)
        list_films = await self._convert_to_model(films_json, FilmListResponse)

        return list_films  # type: ignore

    async def _make_request(self, method: str, url: str, data: dict | None = None) -> dict:
        async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:

            logger.debug(f"Сформирована строка запроса: {url}")
            logger.debug(f"Сформирована data запроса: {data}")

            match method:
                case "get":
                    response = await client.get(url=url)
                    response.raise_for_status()
                case "post":
                    response = await client.post(url=url, json=data)
                    response.raise_for_status()
                case _:
                    raise ValueError(f"Метод: {method} не поддерживается.")

            # Проверяем наличие контента
            if not response.content:
                logger.error(f"Пустой ответ от сервиса {app_config.filmapi.host}")
                raise EmptyServerResponse("Получен пустой ответ от сервиса фильмов")

            response_data = response.json()

            logger.debug(
                f"Получен ответ от сервиса {app_config.filmapi.host}: "
                f"{len(response_data)} фильмов"
            )
            return response_data

    async def _convert_to_model(
        self, json: dict, model: type[GenreResponse] | type[FilmListResponse]
    ) -> list[GenreResponse | FilmListResponse]:
        adapter = TypeAdapter(list[model])
        return adapter.validate_python(json)


def get_film_supplier() -> FilmSupplier:
    return FilmSupplier()
