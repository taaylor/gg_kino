from typing import Any

from core.logger_config import get_logger, log_call
from db.elastic import ElasticDB
from models.models_logic import EmbeddedFilm

logger = get_logger(__name__)


class LoaderFilms:
    """
    Класс для добавления/изменения эмбеддингов фильмов в Elasticsearch.
    """

    def __init__(self, repository: ElasticDB):
        """
        Инициализирует LoaderFilms.

        :param repository: экземпляр ElasticDB для выполнения bulk-операций.
        """
        self.repository = repository

    @staticmethod
    def _build_update_query(
        films_with_decd_embds: list[EmbeddedFilm],
        run_start: int,
    ) -> list[dict[str, Any]]:
        """
        Строит список операций для bulk-обновления документов.

        :param films_with_decd_embds: список объектов EmbeddedFilm.
        :param run_start: метка времени текущего запуска для updated_at.

        :return: список операций для ElasticDB bulk.
        """
        query = [
            {
                "_op_type": "update",
                "_index": "movies",
                "_id": film.id,
                "doc": {
                    "embedding": film.embedding,
                    "updated_at": run_start,
                },
            }
            for film in films_with_decd_embds
        ]
        return query

    @log_call(
        short_input=True,
        short_output=True,
        max_items_for_showing_in_log=10,
    )
    async def execute_loading(
        self,
        films: list[EmbeddedFilm],
        run_start: int,
        batch_size: int,
        raise_on_error: bool = False,
    ) -> tuple[int, list[dict[str, Any]]]:
        """
        Загружает эмбеддинги филмов в ElasticDB через bulk-операции.

        :param films: список объектов EmbeddedFilm для загрузки.
        :param run_start: метка времени текущего запуска для updated_at.
        :param batch_size: размер батча для bulk-операций.
        :param raise_on_error: флаг, поднимать ли исключение при ошибках.

        :return: кортеж (число успешно обновленных документов, список ошибок).
        """
        query = self._build_update_query(films, run_start)
        success_count, errors = await self.repository.bulk_operation(
            query, batch_size, raise_on_error=raise_on_error
        )
        return success_count, errors


def get_loader_films(repository: ElasticDB) -> LoaderFilms:
    """
    Фабрика для получения экземпляра LoaderFilms.

    :param repository: экземпляр ElasticDB для передачи в LoaderFilms.

    :return: новый экземпляр LoaderFilms.
    """
    return LoaderFilms(repository)
