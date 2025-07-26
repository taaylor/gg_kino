from typing import Any

import backoff
import httpx
import requests

# from core.config import app_config
from core.logger_config import get_logger
from httpx import HTTPStatusError, RequestError

logger = get_logger(__name__)


class TransformerFilms:

    def __init__(self, template_embedding: str, url_for_embedding: str):
        self.template_embedding = template_embedding
        self.url_for_embedding = url_for_embedding

    @backoff.on_exception(
        backoff.expo,
        exception=(
            HTTPStatusError,
            RequestError,
        ),
        max_tries=8,
        raise_on_giveup=False,  # после исчерпанных попыток, не прокидывам исключение дальше
        on_backoff=lambda details: logger.warning(  # логируем на каждой итерации backoff
            (
                f"Повтор {details["tries"]} попытка для"
                f" {details["target"].__name__}. Ошибка: {details["exception"]}"
            )
        ),
        on_giveup=lambda details: logger.error(  # логируем когда попытки исчерпаны
            f"Giveup: функция {details["target"].__name__} исчерпала {details["tries"]} попыток"
        ),
    )
    async def async_post_request(
        self,
        url: str,
        json: dict[str, Any] | list[Any],
        timeout: float = 10,
        **kwargs: Any,
    ) -> dict[str, Any] | list[Any]:
        """
        Выполняет POST-запрос с передачей JSON-данных.

        :param url: Адрес запроса.
        :param json: Данные для отправки в теле запроса.
        :param timeout: Таймаут в секундах.
        :param kwargs: Дополнительные параметры httpx.

        :return: Распарсенный JSON-ответ или пустой список в случае ошибки.
        """
        result = []
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url=url, json=json, timeout=timeout, **kwargs)
                response.raise_for_status()
                result = response.json()
            except HTTPStatusError as e:
                logger.error(f"POST запрос по {url} вернул статус код {e.response.status_code}")
                raise e
            except RequestError as e:
                logger.error(f"POST запрос по {url} получил ошибку: {e!r}")
                raise e
            return result

    def _sync_post_request(
        self,
        url: str,
        json: dict[str, Any] | list[Any],
    ):
        payload_response = requests.post(url=url, json=json)
        if payload_response.status_code == 200:
            return payload_response.json()
        return []

    def execute_transform(self, films):
        payload = self._get_payload_for_embedding(films)
        return self._sync_post_request(url=self.url_for_embedding, json=payload)

    def _get_payload_for_embedding(self, films):
        embedding_texts = [
            {
                "id": film["id"],
                "text": self._build_embedding_text(film),
            }
            for film in films
        ]
        return {"objects": embedding_texts}

    def _build_embedding_text(
        self,
        film: list[dict[str, Any]],
    ):
        # TODO: потом переписать, чтобы не словарь передавался, а pydantic модель
        # {title}. {genres}. {description}. {rating_text}.
        # template_embedding = "{title}. {genres}. {description} {rating_text}"
        title = film.get("title", "")
        genres = ", ".join(film.get("genres_names", ""))
        description = film.get("description", None) if film.get("description", None) else ""
        # TODO: вынести уровень рейтинга для High rating в app_config
        rating_text = film.get("imdb_rating", 5)
        if rating_text is not None:
            rating_text = "High rating." if rating_text >= 7 else ""
        # TODO: вынести template_embedding в app_config
        return self.template_embedding.format(
            title=title,
            genres=genres,
            description=description,
            rating_text=rating_text,
        )


def get_transformer_films(template_embedding: str, url_for_embedding: str):
    return TransformerFilms(template_embedding, url_for_embedding)
