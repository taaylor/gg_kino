from core.logger_config import get_logger
from db.elastic import ElasticDB
from models.models_logic import EmbeddedFilm

logger = get_logger(__name__)


class LoaderFilms:

    def __init__(self, repository: ElasticDB):
        self.repository = repository

    @staticmethod
    def _build_update_query(
        films_with_decd_embds: list[EmbeddedFilm],
        run_start: int,
    ) -> list[dict[str, str]]:

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

    async def execute_loading(
        self,
        films: list[EmbeddedFilm],
        run_start: int,
        batch_size: int,
        raise_on_error: bool = False,
    ) -> tuple[int, list[str]]:
        query = self._build_update_query(films, run_start)
        success_count, errors = await self.repository.bulk_operation(
            query, batch_size, raise_on_error=raise_on_error
        )
        return success_count, errors


def get_loader_films(repository: ElasticDB):
    return LoaderFilms(repository)
