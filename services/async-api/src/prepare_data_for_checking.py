"""
Этот файл ревьюрить необязательно, и вникать в код тоже.
Файл нужен для дампа тестовых данных, для демонстрации, что всё работает.
После ревью и проверки, что реализованный код в async-api работает
его можно будет удалить, или перместить в docs/
запускается:
    docker compose -f docker-compose.yml exec async-api python prepare_data_for_checking.py


Что делает этот код:
добавляет в поле "embedding" для документов индекса movies список из 384 float'ов

для таких фильмов (обратите внимание на uuid понадобится при проверке):
(высокое косинусное сходство)
    "3d825f60-9fff-4dfe-b294-1a45fa1e115d",  # [1.0, 0.0, ... <383 ноля>]
    "0312ed51-8833-413f-bff5-0e139c11264a",  # [0.9, 1.0, 0.0 ... <382 ноля>]
    "025c58cd-1b7e-43be-9ffb-8571a613579b",  # [0.9, 0.9, 1.0, 0.0 ... <381 ноля>]
    "cddf9b8f-27f9-4fe9-97cb-9e27d4fe3394",  # и т.д.
    "3b914679-1f5e-4cbd-8044-d13d35d5236c",
    "516f91da-bd70-4351-ba6d-25e16b7713b7",  # т.к. он ARCHIVED его не будет в выборке
    "c4c5e3de-c0c9-4091-b242-ceb331004dfd",
    "4af6c9c9-0be0-4864-b1e9-7f87dd59ee1f",  # т.к. он ARCHIVED его не будет в выборке
    "12a8279d-d851-4eb9-9d64-d690455277cc",
    "118fd71b-93cd-4de5-95a4-e1485edad30e",
    "6ecc7a32-14a1-4da8-9881-bf81f0f09897",

для этих фильмов - список из случайных float'ов в количестве 384
(низкое косинусное сходство)
    "46f15353-2add-415d-9782-fa9c5b8083d5",
    "db5dcded-29da-4c96-91a2-df1407f0a80a",
    "fda827f8-d261-4c23-9e9c-e42787580c4d",
    "57beb3fd-b1c9-4f8a-9c06-2da13f95251c",
    "b1f1e8a6-e310-47d9-a93c-6a7b192bac0e",
    "50fb4de9-e4b3-4aca-9f2f-00a48f12f9b3",
    "6e5cd268-8ce4-45f9-87d2-52f0f26edc9e",
    "b1384a92-f7fe-476b-b90b-6cec2b7a0dce",
    "c9e1f6f0-4f1e-4a76-92ee-76c1942faa97",
    "a7b11817-205f-4e1a-98b5-e3c48b824bc3",
    "1b7d7c64-8be8-47db-8924-23029a9878a9",
"""

import asyncio
import random

from core.config import app_config
from elasticsearch import AsyncElasticsearch

film_uuids_for_near_embedding = [
    "3d825f60-9fff-4dfe-b294-1a45fa1e115d",  # [1.0, 0.0, ... <383 ноля>]
    "0312ed51-8833-413f-bff5-0e139c11264a",  # [0.9, 1.0, 0.0 ... <382 ноля>]
    "025c58cd-1b7e-43be-9ffb-8571a613579b",  # [0.9, 0.9, 1.0, 0.0 ... <381 ноля>]
    "cddf9b8f-27f9-4fe9-97cb-9e27d4fe3394",  # и т.д.
    "3b914679-1f5e-4cbd-8044-d13d35d5236c",
    "516f91da-bd70-4351-ba6d-25e16b7713b7",  # т.к. он ARCHIVED его не будет в выборке
    "c4c5e3de-c0c9-4091-b242-ceb331004dfd",
    "4af6c9c9-0be0-4864-b1e9-7f87dd59ee1f",  # т.к. он ARCHIVED его не будет в выборке
    "12a8279d-d851-4eb9-9d64-d690455277cc",
    "118fd71b-93cd-4de5-95a4-e1485edad30e",
    "6ecc7a32-14a1-4da8-9881-bf81f0f09897",
]

film_uuids_for_far_embedding = [  # [0.313, -0.110, ... <384 случайных float от -1 до 1>]
    "46f15353-2add-415d-9782-fa9c5b8083d5",
    "db5dcded-29da-4c96-91a2-df1407f0a80a",
    "fda827f8-d261-4c23-9e9c-e42787580c4d",
    "57beb3fd-b1c9-4f8a-9c06-2da13f95251c",
    "b1f1e8a6-e310-47d9-a93c-6a7b192bac0e",
    "50fb4de9-e4b3-4aca-9f2f-00a48f12f9b3",
    "6e5cd268-8ce4-45f9-87d2-52f0f26edc9e",
    "b1384a92-f7fe-476b-b90b-6cec2b7a0dce",
    "c9e1f6f0-4f1e-4a76-92ee-76c1942faa97",
    "a7b11817-205f-4e1a-98b5-e3c48b824bc3",
    "1b7d7c64-8be8-47db-8924-23029a9878a9",
]


def prepare_near_vectors(film_uuids_for_near_embedding):
    storage_embeddings = [
        [
            0.0
            for _ in range(app_config.embedding_dims)
            # for _ in range(384)
        ]
        for _ in range(len(film_uuids_for_near_embedding))
    ]
    for i, embd in enumerate(storage_embeddings):
        embd[i] = 1.0
        for before_index in range(i):
            embd[before_index] = 0.9
    return list(zip(film_uuids_for_near_embedding, storage_embeddings))


def prepare_far_vectors(film_uuids_for_far_embedding):
    storage_embeddings = [
        [
            round(random.random(), 3) * random.choice([-1, 1])
            for _ in range(app_config.embedding_dims)
            # for _ in range(384)
        ]
        for _ in range(len(film_uuids_for_far_embedding))
    ]
    return list(zip(film_uuids_for_far_embedding, storage_embeddings))


async def main(data_near_vectors, data_far_vectors):
    es = AsyncElasticsearch(app_config.elastic.get_es_host())
    # "http://{self.host}:{self.port}
    # es = AsyncElasticsearch("http://localhost:9200")
    for data_vectors in [data_near_vectors, data_far_vectors]:
        for movie_id, embedding in data_vectors:
            await es.update(index="movies", id=movie_id, body={"doc": {"embedding": embedding}})
    await es.close()


if __name__ == "__main__":
    data_near_vectors = prepare_near_vectors(film_uuids_for_near_embedding)
    data_far_vectors = prepare_far_vectors(film_uuids_for_far_embedding)
    asyncio.run(main(data_near_vectors, data_far_vectors))
