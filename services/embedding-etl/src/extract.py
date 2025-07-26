from typing import Any

from core.logger_config import get_logger
from db.elastic import ElasticDB, get_repository

logger = get_logger(__name__)


class ExtractorFilms:

    index = "movies"

    def __init__(self, repository: ElasticDB):
        self.repository = repository

    async def execute_search_query(
        self,
        last_run: int,
        run_start: int,  # ! временная мера 1763197091699, потом убрать
        search_after: list[Any] | None,
        batch_size: int,
    ):
        query = self._build_search_query(last_run, run_start)
        return await self.repository.get_list(self.index, query, search_after, batch_size)

    @staticmethod
    def get_films_from_hits(hits_films):
        return [source["_source"] for source in hits_films["hits"]]

    @staticmethod
    def get_films_count(films):
        return films["total"]["value"]

    @staticmethod
    def get_search_after(films):
        return films["hits"]["hits"][-1]["sort"]

    @staticmethod
    def _build_search_query(
        last_run: int,
        run_start: int,
    ):
        query = {
            # "size": 500,
            # "size": 10,
            "sort": [{"updated_at": "asc"}, {"id": "asc"}],
            "query": {
                "range": {
                    "updated_at": {
                        "gt": last_run,
                        # "lte": run_start
                        "lte": 1763197091699,
                    }
                }
            },
            # "query": {"range": {"updated_at": {"gt": 1753198166783, "lte": 1763197091699}}},
        }
        return query


def get_extractor_films(repository: ElasticDB = get_repository()):
    return ExtractorFilms(repository)
