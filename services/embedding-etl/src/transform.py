import base64
from typing import Any

import backoff
import httpx
import numpy as np

# from core.config import app_config
from core.logger_config import get_logger, log_call
from httpx import HTTPStatusError, RequestError
from models.models_logic import EmbeddedFilm, FilmLogic

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
    async def _async_post_request(
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

    @log_call
    async def execute_transformation(self, films: list[FilmLogic]) -> list[EmbeddedFilm]:
        payload = self._get_payload_for_embedding(films)
        filma_with_encd_embds = await self._async_post_request(
            url=self.url_for_embedding,
            json=payload,
        )
        return [
            EmbeddedFilm(id=film["id"], embedding=self._decode_embedding_b64(film["embedding"]))
            for film in filma_with_encd_embds
        ]

    def _get_payload_for_embedding(self, films: list[FilmLogic]):
        embedding_texts = [
            {
                "id": film.id,
                "text": self._build_embedding_text(film),
            }
            for film in films
        ]
        return {"objects": embedding_texts}

    def _build_embedding_text(
        self,
        film: FilmLogic,
    ):
        return self.template_embedding.format(
            title=film.title,
            genres=film.genres_names,
            description=film.description,
            rating_text=film.imdb_rating,
        )

    @staticmethod
    def _decode_embedding_b64(emb: str) -> list[float]:
        embedding_bytes = base64.b64decode(emb)
        return list(np.frombuffer(embedding_bytes, dtype=float))


def get_transformer_films(template_embedding: str, url_for_embedding: str):
    return TransformerFilms(template_embedding, url_for_embedding)
