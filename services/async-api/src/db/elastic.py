import logging
from uuid import UUID

from db.database import BaseDB, PaginateBaseDB
from elasticsearch import AsyncElasticsearch, ConnectionError, ConnectionTimeout
from utils.decorators import backoff, elastic_handler_exeptions

logger = logging.getLogger(__name__)


class ElasticDB(BaseDB):
    """Класс для работы с хранилищем ElasticSearch"""

    def __init__(
        self,
        elastic: AsyncElasticsearch,
    ):
        self.elastic = elastic

    @elastic_handler_exeptions
    @backoff(exception=(ConnectionError, ConnectionTimeout))
    async def get_object_by_id(self, index: str, object_id: UUID, **kwargs) -> dict | None:
        """Получить детальную информацию об объекте из ElasticSearch по UUID."""
        logger.debug(f"Получаю детальную информацию из ElasticSearch по объекту {object_id=}")
        data = await self.elastic.get(index=index, id=str(object_id), **kwargs)
        return data.get("_source")

    @elastic_handler_exeptions
    @backoff(exception=(ConnectionError, ConnectionTimeout))
    async def get_list(
        self,
        index: str,
        body: dict,
        page_number: int | None = None,
        page_size: int | None = None,
        **kwargs,
    ) -> list[dict]:
        """Получить список объектов из ElasticSearch по фильтрации переданных данных"""
        logger.debug(f"Получаю список объектов из ElasticSearch по запросу:\n{body}.")
        if page_size and page_number:
            body["from"] = (page_number - 1) * page_size
            body["size"] = page_size
        document = await self.elastic.search(index=index, body=body, **kwargs)
        return [source["_source"] for source in document["hits"]["hits"]]


class PaginateElasticDB(PaginateBaseDB):
    """Класс, реализующий пагинацию через обёртку над ElasticDB"""

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic
        self._base_db = ElasticDB(elastic)

    async def get_object_by_id(self, index: str, object_id: UUID, **kwargs) -> dict | None:
        return await self._base_db.get_object_by_id(index, object_id, **kwargs)

    async def get_list(self, index: str, body: dict, **kwargs) -> list[dict]:
        return await self._base_db.get_list(index, body=body, **kwargs)

    @elastic_handler_exeptions
    @backoff(exception=(ConnectionError, ConnectionTimeout))
    async def get_count(self, index: str, **kwargs) -> int:
        logger.debug(f"Получаю количество документов в индексе {index} ElasticSearch.")
        result = await self.elastic.count(index=index, **kwargs)
        if result is None:
            return 0
        return int(result.get("count"))


es: AsyncElasticsearch | None = None


async def get_repository() -> BaseDB:
    if es is None:
        raise ValueError("Elasticsearch не инициализирован")
    return ElasticDB(es)


async def get_paginate_repository() -> PaginateBaseDB:
    if es is None:
        raise ValueError("Elasticsearch не инициализирован")
    return PaginateElasticDB(es)
