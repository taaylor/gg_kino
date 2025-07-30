import base64

import numpy as np
from core.logger_config import get_logger, log_call
from http_process import HttpClient, get_http_client
from models.models_logic import EmbeddedFilm, FilmLogic

logger = get_logger(__name__)


class TransformerFilms:
    """
    Класс для преобразования данных фильмов в векторные эмбеддинги.
    """

    def __init__(
        self,
        template_embedding: str,
        url_for_embedding: str,
        http_clent: HttpClient,
    ):
        """
        Инициализирует TransformerFilms.

        :param template_embedding: шаблон текста для генерации embedding.
        :param url_for_embedding: URL сервиса для получения embedding.
        """
        self.template_embedding = template_embedding
        self.url_for_embedding = url_for_embedding
        self.http_clent = http_clent

    @log_call(
        short_input=True,
        short_output=True,
        max_items_for_showing_in_log=10,
    )
    async def execute_transformation(self, films: list[FilmLogic]) -> list[EmbeddedFilm]:
        """
        Основной метод для выполнения трансформации.

        :param films: список объектов FilmLogic.

        :return: список объектов EmbeddedFilm с векторами embedding.
        """
        payload = self._get_payload_for_embedding(films)
        filma_with_encd_embds = await self.http_clent.async_post_request(
            url=self.url_for_embedding,
            json=payload,
        )
        return [
            EmbeddedFilm(id=film["id"], embedding=self._decode_embedding_b64(film["embedding"]))
            for film in filma_with_encd_embds
        ]

    def _get_payload_for_embedding(self, films: list[FilmLogic]) -> dict[str, dict[str, str]]:
        """
        Формирует JSON-пayload для сервиса embedding.

        :param films: список объектов FilmLogic.

        :return: словарь с ключом "objects" для POST-запроса.
        """
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
    ) -> str:
        """
        Собирает текст для эмбеддинга по шаблону.

        :param film: объект FilmLogic.

        :return: строка с данными фильма.
        """
        return self.template_embedding.format(
            title=film.title,
            genres=film.genres_names,
            description=film.description,
            rating_text=film.imdb_rating,
        )

    @staticmethod
    def _decode_embedding_b64(emb: str) -> list[float]:
        """
        Декодирует base64-строку в список float.

        :param emb: base64-представление embedding.

        :return: список float значений эмбеддинга.
        """
        embedding_bytes = base64.b64decode(emb)
        return [float(v) for v in np.frombuffer(embedding_bytes, dtype=np.float32)]


def get_transformer_films(
    template_embedding: str,
    url_for_embedding: str,
    http_clent: HttpClient = get_http_client(),
) -> TransformerFilms:
    """
    Фабрика для получения экземпляра TransformerFilms.

    :param template_embedding: шаблон текста для embedding.
    :param url_for_embedding: адрес сервиса embedding.

    :return: новый экземпляр TransformerFilms.
    """
    return TransformerFilms(template_embedding, url_for_embedding, http_clent)
