import asyncio
import json
import random
import uuid
from datetime import datetime
from string import printable

import asyncpg

DSN = "postgresql://postgres:postgres@localhost:5432/pg_db"
BATCH_SIZE = 100_000  # 100 тыс.

COUNT_RECORDS = 10_000_000  # 10 млн.

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


async def insert_one_rating(user_film_ids):
    sql = """
    INSERT INTO rating (id, user_id, film_id, created_at, updated_at, score)
    VALUES ($1, $2, $3, $4, $5, $6)
    ON CONFLICT (film_id, user_id) DO NOTHING
    """
    async with asyncpg.create_pool(
        dsn=DSN,
        min_size=1,
        max_size=10
    ) as pool:
        async with pool.acquire() as conn:
            for _ in range(COUNT_BATCHES):
                batch = []
                for counter in range(1, BATCH_SIZE + 1):
                    if counter % BATCH_SIZE == 0:
                        try:
                            user_id, film_id = next(user_film_ids)
                        except StopIteration:
                            user_id, film_id = uuid.uuid4(), uuid.uuid4()
                    else:
                        user_id, film_id = uuid.uuid4(), uuid.uuid4()
                    batch.append(
                        (
                            uuid.uuid4(),
                            user_id,
                            film_id,
                            datetime.now(),
                            datetime.now(),
                            random.randint(1, 10),
                        )
                    )
                await conn.copy_records_to_table(
                    'rating',
                    records=batch,
                    columns=['id', 'user_id', 'film_id',
                             'created_at', 'updated_at', 'score']
                )

async def create_indexes_after_load():
    pool = await asyncpg.create_pool(dsn=DSN, min_size=1, max_size=1)
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS
            rating_user_id_film_id_idx ON rating (film_id, user_id)
        """)
        # создаём вторичные индексы
        await conn.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS rating_user_id_idx ON rating (user_id)
        """)
        await conn.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS rating_film_id_idx ON rating (film_id)
        """)
    await pool.close()

async def main(user_film_ids):
    await insert_one_rating(user_film_ids)
    await create_indexes_after_load()
    print("Bulk load и создание индексов завершены")

if __name__ == "__main__":
    user_ids = [uuid.uuid4() for _ in range(COUNT_BATCHES // 10)]
    film_ids = [uuid.uuid4() for _ in range(COUNT_BATCHES // 10)]
    with open("user_film_ids.json", "w", encoding="utf-8") as f:
        json.dump([{"user_id": str(user_id), "film_id": str(film_id)} for user_id,
                  film_id in get_pair_user_id_film_id(user_ids, user_ids, )], f, indent=5)
    user_film_ids = get_pair_user_id_film_id(user_ids, user_ids, )
    asyncio.run(main(user_film_ids))
    print("Вставка одной записи выполнена")
