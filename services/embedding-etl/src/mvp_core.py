"""
while True:
    result = <запрос в ES>
    # делаем такой запрос на python:
    # POST http://localhost:9200/movies/_search
    # Content-Type: application/json

    # {
    #   "size": 500,
    #   "sort": [
    #     { "updated_at": "asc" },
    #     { "_id":         "asc" }
    #   ],
    #   "query": {
    #     "range": {
    #       "updated_at": {
    #         "gt":  "2025-07-20T03:00:00Z",   ← last_run
    #         "lte": "2025-07-21T00:00:00Z"    ← run_start
    #       }
    #     }
    #   }
    # }
    if len(result) == 0:
        last_run = run_start
        # сохраняем в кеш last_run
        break
    else:
        # выполняем запрос в embedding-service для получения поля embedding
        # и после, обновляем документы в ES которые достали из того запроса,
        # присваивая updated_at и embedding




! вариант декодирования
import numpy as np
import base64

embedding_bytes = base64.b64decode(embedding_base64) # сюда передаем вектор в base64
embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
embedding_2 = np.frombuffer(embedding_bytes, dtype=float)

"""

# last_run = load_from_cache()
# run_start = current_time()

# search_after = None

# while True:
#     query = {
#         "size": 500,
#         "sort": [
#             { "updated_at": "asc" },
#             { "_id": "asc" }
#         ],
#         "query": {
#             "range": {
#                 "updated_at": {
#                     "gt": last_run,
#                     "lte": run_start
#                 }
#             }
#         }
#     }

#     if search_after is not None:
#         query["search_after"] = search_after

#     result = elasticsearch_search(query)

#     if not result["hits"]["hits"]:
#         save_to_cache(last_run=run_start)
#         break

#     for doc in result["hits"]["hits"]:
#         # Сформировать текст для embedding
#         text = build_embedding_text(doc["_source"])

#         # Получить embedding
#         embedding = get_embedding_from_service(text)

#         # Обновить документ в ES
#         update_doc_in_elasticsearch(
#             doc_id=doc["_id"],
#             body={
#                 "doc": {
#                     "embedding": embedding,
#                     "updated_at": doc["_source"]["updated_at"]
# # чтобы не терять контроль
#                 }
#             }
#         )

#     # Получить search_after из последнего документа
#     search_after = result["hits"]["hits"][-1]["sort"]

import asyncio
import base64
import time

# import logging
from typing import Any

import backoff
import httpx
import numpy as np
from core.config import app_config
from core.logger_config import get_logger
from db.cache import get_cache
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from httpx import HTTPStatusError, RequestError
from redis.asyncio import Redis

# from pprint import pprint as pp


logger = get_logger(__name__)

RUN_START = "embedding-etl:unix_timestamp:run_start:"
LAST_RUN = "embedding-etl:unix_timestamp:last-run:"
URL_TO_EMBEDDING_LOC = "http://localhost:8000/embedding-service/api/v1/embedding/fetch-embeddings"
URL_TO_EMBEDDING_PROD = (
    "http://embedding-service:8000/embedding-service/api/v1/embedding/fetch-embeddings"
)


@backoff.on_exception(
    backoff.expo,
    exception=(
        HTTPStatusError,
        RequestError,
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
async def post_request(
    url: str,
    json_data: dict[str, Any] | list[Any],
    timeout: float = 10,
    **kwargs: Any,
) -> dict[str, Any] | list[Any]:
    """
    Выполняет POST-запрос с передачей JSON-данных.

    :param url: Адрес запроса.
    :param json_data: Данные для отправки в теле запроса.
    :param timeout: Таймаут в секундах.
    :param kwargs: Дополнительные параметры httpx.

    :return: Распарсенный JSON-ответ или пустой список в случае ошибки.
    """
    result = []
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url=url, json=json_data, timeout=timeout, **kwargs)
            response.raise_for_status()
            result = response.json()
        except HTTPStatusError as e:
            logger.error(f"POST запрос по {url} вернул статус код {e.response.status_code}")
            raise e
        except RequestError as e:
            logger.error(f"POST запрос по {url} получил ошибку: {e!r}")
            raise e
        return result


async def get_embedding_from_service(data_for_sending):

    pass


def build_embedding_text(doc):
    # TODO: потом переписать, чтобы не словарь передавался, а pydantic модель
    # {title}. {genres}. {description}. {rating_text}.
    template_embedding = "{title}. {genres}. {description} {rating_text}"
    title = doc.get("title", "")
    genres = ", ".join(doc.get("genres_names", ""))
    description = doc.get("description", None) if doc.get("description", None) else ""
    # TODO: вынести уровень рейтинга для High rating в app_config
    rating_text = "High rating." if doc.get("imdb_rating", 5) >= 7 else ""
    # TODO: вынести template_embedding в app_config
    return template_embedding.format(
        title=title,
        genres=genres,
        description=description,
        rating_text=rating_text,
    )


def decode_embedding_b64(emb):
    embedding_bytes = base64.b64decode(emb)
    return list(map(float, np.frombuffer(embedding_bytes, dtype=np.float32)))


async def main():
    # return f"http://{self.host}:{self.port}"
    elastic_client = AsyncElasticsearch("http://localhost:9200")
    cache_conn = Redis(
        host="localhost",
        # host=app_config.redis.host,
        port=app_config.redis.port,
        db=app_config.redis.db,
        decode_responses=True,
        username=app_config.redis.user,
        password=app_config.redis.password,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_error=False,
        retry_on_timeout=False,
    )
    cache = await get_cache(cache_conn)
    if last_run := await cache.get(LAST_RUN):
        logger.info(f"Время last_run: {last_run}")
    else:
        last_run = int(time.time() * 1000)
    # run_start = int(time.time() * 1000)
    search_after = None
    query = {
        # "size": 500,
        "size": 10,
        "sort": [{"updated_at": "asc"}, {"id": "asc"}],
        # "query": {"range": {"updated_at": {"gt": last_run, "lte": run_start}}},
        "query": {"range": {"updated_at": {"gt": 1753198166783, "lte": 1763197091699}}},
    }
    if search_after is not None:
        query["search_after"] = search_after
    documents = await elastic_client.search(index="movies", body=query)
    parsed_documents = [source["_source"] for source in documents["hits"]["hits"]]
    embedding_texts = [
        {
            "id": doc["id"],
            "text": build_embedding_text(doc),
        }
        for doc in parsed_documents
    ]
    payload = {"objects": embedding_texts}
    """
    async def post_request(
    url: str,
    json_data: dict[str, Any] | list[Any],

    """
    payload_response = await post_request(
        url=URL_TO_EMBEDDING_LOC,
        json_data=payload,
    )
    data_for_update = [
        {
            "_op_type": "update",
            "_index": "movies",
            "_id": item["id"],
            # "doc": {"embedding": decode_embedding_b64(item["embedding"])},
            "doc": {
                "embedding": [
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                ]
            },
        }
        for item in payload_response
    ]
    success_count, errors = await async_bulk(
        client=elastic_client,
        actions=data_for_update,
        chunk_size=100,
        max_retries=3,
        raise_on_error=True,
    )
    # вычисляем вектор с помощью декодирования
    # обновляем данные в es
    """
    success_count, errors = await async_bulk(
        client=es,
        actions=actions,
        # опциональные параметры:
        chunk_size=500,      # сколько действий в одном чанке
        max_retries=3,       # сколько попыток в случае ошибок
        raise_on_error=False # не бросать исключение, а возвращать ошибки в списке
    )

    return success_count, errors
    """
    logger.info([doc["id"] for doc in parsed_documents])
    # a = 1

    # a = 1
    await elastic_client.close()
    # await cache_conn.close()
    await cache_conn.aclose()
    return parsed_documents


if __name__ == "__main__":
    asyncio.run(main())
