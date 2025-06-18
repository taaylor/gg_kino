import uuid
from datetime import datetime

import psycopg

# DSN: подставьте свои параметры при необходимости
DSN = "postgresql://postgres:postgres@postgres:5432/pg_db"

def insert_one_rating():
    # Генерируем значения
    new_id = uuid.uuid4()
    user_id = uuid.uuid4()
    film_id = uuid.uuid4()
    now = datetime.now()
    score = 5  # пример оценки от 1 до 10

    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO rating (id, user_id, film_id, created_at, updated_at, score)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (film_id, user_id) DO NOTHING
                """,
                (new_id, user_id, film_id, now, now, score)
            )
            # при выходе из with conn.cursor() и with psycopg.connect() транзакция зафиксируется автоматически

if __name__ == "__main__":
    insert_one_rating()
    print("Вставка одной записи выполнена")
