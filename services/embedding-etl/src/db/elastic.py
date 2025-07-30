import logging
from typing import Any

import backoff
from elasticsearch import AsyncElasticsearch, ConnectionError, ConnectionTimeout
from elasticsearch.helpers import async_bulk
from utils.decorators import elastic_handler_exeptions

logger = logging.getLogger(__name__)


class ElasticDB:
    """Класс для работы с хранилищем ElasticSearch"""

    def __init__(
        self,
        elastic: AsyncElasticsearch,
    ):
        self.elastic = elastic

    @elastic_handler_exeptions
    @backoff.on_exception(
        backoff.expo,
        exception=(
            ConnectionError,
            ConnectionTimeout,
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
        return document["hits"]

    @elastic_handler_exeptions
    @backoff.on_exception(
        backoff.expo,
        exception=(
            ConnectionError,
            ConnectionTimeout,
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
    async def bulk_operation(
        self,
        actions: list[dict[str, str]],
        batch_size: int = 10,
        max_retries: int = 3,
        raise_on_error: bool = False,
    ) -> tuple[int, list[dict[str, Any]]]:
        success_count, errors = await async_bulk(
            client=self.elastic,
            actions=actions,
            chunk_size=batch_size,  # максимальный размер чанка
            max_retries=max_retries,  # кол-во попыток в случае ошибок
            raise_on_error=raise_on_error,  # не бросать исключение, а возвращать ошибки в списке
        )
        return success_count, errors

    async def close_elastic(self):
        await self.elastic.close()


es: AsyncElasticsearch | None = None


def get_elastic_repository() -> ElasticDB:
    if es is None:
        raise ValueError("Elasticsearch не инициализирован")
    return ElasticDB(es)
