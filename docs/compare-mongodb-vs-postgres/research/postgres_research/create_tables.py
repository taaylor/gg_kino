import asyncio
import random
import uuid
from datetime import datetime
from string import printable
from typing import Any

import asyncpg
from pydantic import BaseModel

BATCH_SIZE = 100_000  # 100 тыс.

COUNT_RECORDS = 10_000_000  # 10 млн.

COUNT_BATCHES = COUNT_RECORDS // BATCH_SIZE

EXTRA_FIELDS = {
    "score": lambda: random.randint(1, 10),
    "comment": lambda: printable,
}

class Postgres(BaseModel):
    host: str = "postgres"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    db: str = "pg_db"

    @property
    def SYNC_DATABASE_URL(self):
        # return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
        return "postgresql://postgres:postgres@localhost:5432/pg_db"

app_config = Postgres()

user_ids = [uuid.uuid4() for _ in range(COUNT_BATCHES // 10)]
film_ids = [uuid.uuid4() for _ in range(COUNT_BATCHES // 10)]


def get_pair_user_id_film_id(film_ids, user_ids):
    yield from (
        (f_id, u_id,)
        for f_id in film_ids
        for u_id in user_ids
    )


def get_record(counter: int, pairs_film_user_ids, extra_field_value: Any):
    if counter % BATCH_SIZE == 0:
        user_id, film_id = uuid.uuid4(), uuid.uuid4()
    else:
        user_id, film_id = next(pairs_film_user_ids)
    return (
        uuid.uuid4(),
        user_id,
        film_id,
        datetime.now(),
        datetime.now(),
        extra_field_value  # random.randint(1, 10)
    )


async def insert_data(db_name: str, extra_field: str):
    # создаём пул
    async with asyncpg.create_pool(
        dsn=app_config.SYNC_DATABASE_URL,
        min_size=1,
        max_size=10
    ) as pool:
        # берём соединение из пула
        async with pool.acquire() as conn:
            # внутри транзакции (необязательно, но часто нужно)
            async with conn.transaction():
                pair_ids = get_pair_user_id_film_id(film_ids, user_ids)
                sql = f"""
                    INSERT INTO {db_name}(id, user_id, film_id, created_at, updated_at, {extra_field})
                    VALUES($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (film_id, user_id) DO NOTHING
                    """
                for _ in range(COUNT_BATCHES):
                    batch = []
                    for counter in range(1, BATCH_SIZE + 1):
                        batch.append(
                            get_record(
                                counter,
                                pair_ids,
                                EXTRA_FIELDS[extra_field]()
                            )
                        )
                    await conn.executemany(sql, batch)
                print("Вставка завершена")


if __name__ == "__main__":
    asyncio.run(insert_data("rating", "score"))
