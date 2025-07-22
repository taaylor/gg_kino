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

import time

from core.config import app_config
from core.logger_config import get_logger
from db.cache import get_cache
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

# from pprint import pprint as pp


logger = get_logger(__name__)

RUN_START = "embedding-etl:unix_timestamp:run_start:"
LAST_RUN = "embedding-etl:unix_timestamp:last-run:"


async def main():
    elastic_client = AsyncElasticsearch(app_config.elastic.get_es_host)
    cache_conn = Redis(
        host=app_config.redis.host,
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
    run_start = int(time.time() * 1000)
    search_after = None
    query = {
        # "size": 500,
        "size": 10,
        "sort": [{"updated_at": "asc"}, {"id": "asc"}],
        "query": {"range": {"updated_at": {"gt": last_run, "lte": run_start}}},
    }
    if search_after is not None:
        query["search_after"] = search_after
    documents = await elastic_client.search(index="movies", body=query)
    parsed_documents = [source["_source"] for source in documents["hits"]["hits"]]
    return parsed_documents
