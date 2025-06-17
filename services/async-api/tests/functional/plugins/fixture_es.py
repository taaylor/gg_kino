from typing import Any

import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from tests.functional.core.settings import test_conf


@pytest_asyncio.fixture(name="es_client", scope="session")
async def es_client():
    es_client = AsyncElasticsearch(hosts=test_conf.elastic.es_host, verify_certs=False)
    yield es_client
    await es_client.close()


def _create_bulk_query(
    index: str,
    es_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    bulk_query = []
    for item in es_data:
        data = {
            "_index": index,
            "_id": item.get("id"),
            "_source": item,
        }
        bulk_query.append(data)
    return bulk_query


@pytest_asyncio.fixture(name="es_write_data", scope="function")
async def es_write_data(es_client: AsyncElasticsearch):
    # Список для хранения индексов, которые нужно удалить
    indices_to_delete = []

    async def inner(data: list[dict], index: str, mapping: dict):
        # Добавляем индекс в список для удаления
        indices_to_delete.append(index)

        # Удаляем индекс, если он существует
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index)

        # Создаем индекс с заданным маппингом
        await es_client.indices.create(index=index, **mapping)

        prepared_data = _create_bulk_query(index=index, es_data=data)

        # Записываем данные в индекс
        _, failed = await async_bulk(
            client=es_client,
            actions=prepared_data,
            refresh="wait_for",
        )

        if failed:
            raise Exception("Ошибка записи данных в Elasticsearch", errors=failed)

    yield inner
    # Удаляем индексы после завершения теста
    for index in indices_to_delete:
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index)
