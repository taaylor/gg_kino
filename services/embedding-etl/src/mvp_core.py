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

# import json
import time

# import backoff
# import httpx
from connectors import lifespan
from core.config import app_config
from core.logger_config import get_logger
from db.cache import get_cache
from db.elastic import get_elastic_repository

# from elasticsearch import AsyncElasticsearch
# from elasticsearch.helpers import async_bulk
from extract import get_extractor_films
from load import get_loader_films

# from httpx import HTTPStatusError, RequestError
# from redis.asyncio import Redis
from transform import get_transformer_films

# import logging
# from typing import Any


# from pprint import pprint as pp


logger = get_logger(__name__)

RUN_START = "embedding-etl:unix_timestamp:run_start"
LAST_RUN = "embedding-etl:unix_timestamp:last-run"
URL_TO_EMBEDDING_LOC = "http://localhost:8007/embedding-service/api/v1/embedding/fetch-embeddings"
URL_TO_EMBEDDING_PROD = (
    "http://embedding-service:8007/embedding-service/api/v1/embedding/fetch-embeddings"
)


async def main():
    async with lifespan():
        cache = await get_cache()
        elastic_repository = get_elastic_repository()
        if last_run := await cache.get(LAST_RUN):
            last_run = int(last_run)
            logger.info(f"Время last_run: {last_run}")
        else:
            last_run = int(time.time() * 1000)
        run_start = int(time.time() * 1000)
        extractor = get_extractor_films(elastic_repository)
        transformer = get_transformer_films(
            app_config.template_embedding,
            app_config.url_for_embedding_loc,
        )
        loader = get_loader_films(elastic_repository)
        while True:
            films = await extractor.execute_extraction(
                last_run,
                run_start,
                batch_size=10,
            )
            if not len(films):
                break
            transformed_films = transformer.execute_transformation(films)
            success_count, errors = await loader.execute_loading(
                films=transformed_films,
                run_start=run_start,
                batch_size=100,
            )
            logger.info(
                (
                    f"Документы успешно обновились в количестве {success_count}"
                    f"количество ошибок: {len(errors)}"
                )
            )
            if errors:
                logger.error(f"Ошибки при обновлении: {errors}")

        await cache.background_set(
            key=LAST_RUN,
            value=str(run_start),
            expire=app_config.cache_expire_in_seconds,
        )
        logger.info(
            (
                "ETL успешно отработал, кол-во шибок <поместить кол-во ошибок>"
                "Новое время сохранено в Redis:"
                f" LAST RUN - {LAST_RUN}:{run_start}"
            )
        )
    return True


if __name__ == "__main__":
    asyncio.run(main())
