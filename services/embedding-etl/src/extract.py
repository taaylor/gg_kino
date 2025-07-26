from core.logger_config import get_logger
from db.elastic import ElasticDB
from models.models_logic import FilmLogic

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
    ) -> list[FilmLogic]:
        query = self._build_search_query(last_run, run_start)
        films_list = await self.repository.get_list(
            self.index, query, self.search_after, batch_size
        )
        self.search_after = films_list["hits"]
        return [
            FilmLogic(
                id=source["_source"].get("id"),
                title=source["_source"].get("title"),
                description=source["_source"].get("description", ""),
                imdb_rating=source["_source"].get("imdb_rating", 5.0),
                genres_names=source["_source"].get("genres_names", []),
            )
            for source in films_list["hits"]
        ]

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
            # загружаем только эти поля из документа
            "_source": [
                "id",
                "title",
                "genres_names",
                "description",
                "imdb_rating",
                "updated_at",
            ],
            "sort": [{"updated_at": "asc"}, {"id": "asc"}],
            "query": {
                "bool": {
                    "should": [  # should - условие OR
                        {  # или в дипозоне: last_run < updated_at <= run_start
                            "range": {
                                "updated_at": {
                                    "gt": last_run,
                                    "lte": run_start,
                                }
                            }
                        },
                        {  # или не должно быть присвоено значение для поля embedding
                            "bool": {"must_not": {"exists": {"field": "embedding"}}}
                        },
                    ],
                    # минимум 1но совпадение из условия should (OR)
                    "minimum_should_match": 1,
                }
            },
        }
        # query = {
        #     "_source": [
        #         "id",
        #         "title",
        #         "genres_names",
        #         "description",
        #         "imdb_rating",
        #         "updated_at",
        #     ],
        #     "sort": [
        #         {"updated_at": "asc"},
        #         {"id": "asc"},
        #     ],
        #     "query": {
        #         "bool": {
        #             "should": [
        #                 {
        #                     "range": {
        #                         "updated_at": {
        #                             "gt": last_run,
        #                             "lte": 1763197091699,
        #                         }
        #                     }
        #                 },
        #                 {
        #                     "bool": {
        #                         "must_not": {
        #                             "exists": {
        #                                 "field": "embedding"
        #                             }
        #                         }
        #                     }
        #                 }
        #             ],
        #             "minimum_should_match": 1
        #         }
        #     }
        # }
        # "query": {
        #     "range": {
        #         "updated_at": {
        #             "gt": last_run,
        #             # "lte": run_start
        #             "lte": 1763197091699,
        #         }
        #     }
        # },
        # "query": {"range": {"updated_at": {"gt": 1753198166783, "lte": 1763197091699}}},
        # query = {
        #     "_source": [
        #         "id",
        #         "title",
        #         "genres_names",
        #         "description",
        #         "imdb_rating",
        #         "updated_at",
        #     ],
        #     "sort": [{"updated_at": "asc"}, {"id": "asc"}],
        #     "query": {
        #         "range": {
        #             "updated_at": {
        #                 "gt": last_run,
        #                 # "lte": run_start
        #                 "lte": 1763197091699,
        #             }
        #         }
        #     },
        #     # "query": {"range": {"updated_at": {"gt": 1753198166783, "lte": 1763197091699}}},
        # }
        return query


def get_extractor_films(repository: ElasticDB):
    return ExtractorFilms(repository)
