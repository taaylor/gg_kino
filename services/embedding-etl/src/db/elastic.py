import logging
from typing import Any

# from core.config import app_config
from elasticsearch import AsyncElasticsearch, ConnectionError, ConnectionTimeout
from utils.decorators import backoff, elastic_handler_exeptions

logger = logging.getLogger(__name__)


class ElasticDB:
    """Класс для работы с хранилищем ElasticSearch"""

    def __init__(
        self,
        elastic: AsyncElasticsearch,
    ):
        self.elastic = elastic

    @elastic_handler_exeptions
    @backoff(exception=(ConnectionError, ConnectionTimeout))
    async def get_list(
        self,
        index: str,
        body: dict,
        search_after: list[Any] | None,
        batch_size: int = 10,
        **kwargs,
    ) -> list[dict]:
        """Получить список объектов из ElasticSearch по фильтрации переданных данных"""
        if search_after is not None:
            body["search_after"] = search_after
        body["size"] = batch_size
        logger.debug(f"Получаю список объектов из ElasticSearch по запросу:\n{body}.")
        document = await self.elastic.search(index=index, body=body, **kwargs)
        # return [source["_source"] for source in document["hits"]["hits"]]
        return document["hits"]


def get_repository() -> ElasticDB:
    elastic_client = AsyncElasticsearch("http://localhost:9200")
    # elastic_client = AsyncElasticsearch(app_config.elastic.get_es_host)
    return ElasticDB(elastic_client)
