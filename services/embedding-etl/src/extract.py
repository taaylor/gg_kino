from core.logger_config import get_logger
from db.elastic import ElasticDB

logger = get_logger(__name__)


class ExtractorFilms:

    index = "movies"

    def __init__(self, repository: ElasticDB):
        self.repository = repository
        self._search_after = None

    async def execute_extraction(
        self,
        last_run: int,
        run_start: int,  # ! временная мера 1763197091699, потом убрать
        batch_size: int,
    ):
        query = self._build_search_query(last_run, run_start)
        films_list = await self.repository.get_list(
            self.index, query, self.search_after, batch_size
        )
        self.search_after = films_list["hits"]
        return [source["_source"] for source in films_list["hits"]]

    @staticmethod
    def get_films_from_hits(hits_films):
        return [source["_source"] for source in hits_films["hits"]]

    @staticmethod
    def get_films_count(films):
        return films["total"]["value"]

    @property
    def search_after(self):
        return self._search_after

    @search_after.setter
    def search_after(self, hits: list[dict]):
        if not hits:
            self._search_after = None
        else:
            self._search_after = hits[-1]["sort"]

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


def get_extractor_films(repository: ElasticDB):
    return ExtractorFilms(repository)
