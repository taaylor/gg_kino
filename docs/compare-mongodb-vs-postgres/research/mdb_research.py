import asyncio
import json
import random
import uuid
from datetime import datetime
from string import printable

import motor.motor_asyncio
from bson.binary import Binary, UuidRepresentation

# Настройки
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "kinoservice"
COLLECTION_NAME = "ratingCollection"
# размер одного батча; можно экспериментировать (1k–10k)
BATCH_SIZE = 100_000
# BATCH_SIZE = 100_00
COUNT_RECORDS = 10_000_000
COUNT_BATCHES = COUNT_RECORDS // BATCH_SIZE

EXTRA_FIELDS = {
    "score": lambda: random.randint(1, 10),
    "comment": lambda: printable,
}


def get_pair_user_id_film_id(user_ids, film_ids,):
    yield from (
        (u_id, f_id,)
        for u_id in user_ids
        for f_id in film_ids
    )


def make_document(user_id, film_id):
    """
    Генерирует один документ по вашей схеме.
    При вставке Python UUID будет сохранён как Binary(subtype=4) по умолчанию в PyMongo/Motor
    (если драйвер настроен на uuidRepresentation='standard').
    """
    return {
        "_id": Binary.from_uuid(uuid.uuid4(), UuidRepresentation.STANDARD),
        "user_id": Binary.from_uuid(user_id, UuidRepresentation.STANDARD),
        "film_id": Binary.from_uuid(film_id, UuidRepresentation.STANDARD),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "score": random.randint(1, 10),
    }


async def insert_bulk(user_film_ids):
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    coll = db[COLLECTION_NAME]

    docs_batch = []
    for counter in range(1, COUNT_RECORDS + 1):
        if counter % BATCH_SIZE == 0:
            try:
                user_id, film_id = next(user_film_ids)
            except StopIteration:
                user_id, film_id = uuid.uuid4(), uuid.uuid4()
        else:
            user_id, film_id = uuid.uuid4(), uuid.uuid4()
        docs_batch.append(
            {
                "_id": Binary.from_uuid(uuid.uuid4(), UuidRepresentation.STANDARD),
                "user_id": Binary.from_uuid(user_id, UuidRepresentation.STANDARD),
                "film_id": Binary.from_uuid(film_id, UuidRepresentation.STANDARD),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "score": random.randint(1, 10),
            }
        )
        if len(docs_batch) >= BATCH_SIZE:
            try:
                # ordered=False позволит быстрее, не прерываясь на ошибках дубликатов
                await coll.insert_many(docs_batch, ordered=False)
                print(f"Inserted {counter}")
            except Exception as e:
                print("Exception occuried")
            docs_batch.clear()
    # Оставшиеся
    if docs_batch:
        try:
            await coll.insert_many(docs_batch, ordered=False)
            print("Inserted last")
        except Exception:
            print("Exception occuried")


    client.close()

if __name__ == "__main__":
    user_ids = [uuid.uuid4() for _ in range(COUNT_BATCHES // 10)]
    film_ids = [uuid.uuid4() for _ in range(COUNT_BATCHES // 10)]
    with open("mongo_user_film_ids.json", "w", encoding="utf-8") as f:
        json.dump([{"user_id": str(user_id), "film_id": str(film_id)} for user_id,
                  film_id in get_pair_user_id_film_id(user_ids, user_ids, )], f, indent=5)
    user_film_ids = get_pair_user_id_film_id(user_ids, user_ids, )

    asyncio.run(insert_bulk(user_film_ids))
