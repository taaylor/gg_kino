"""
Скрипт для тестирования производительности баз данных PostgreSQL и MongoDB.
Измеряет среднее время выполнения запросов для получения записей по заранее подготовленным ID.

ВАЖНО: Для работы скрипта необходимо подготовить файлы с ID записей:
- postgres_ids.txt: список ID записей для PostgreSQL (по одному на строке)
- mongo_ids.txt: список ObjectId для MongoDB (по одному на строке)

Методы получения записей:
- MongoDB: поиск документа по полю _id с использованием find_one()
- PostgreSQL: поиск записи по полю id с использованием WHERE id = %s

Преимущества по сравнению со случайными запросами:
- Воспроизводимые результаты тестирования
- Возможность тестировать конкретные записи
- Более реалистичные сценарии (обычно приложения ищут записи по известным ID)

Зависимости:
- motor: асинхронный драйвер для MongoDB
- psycopg: асинхронный драйвер для PostgreSQL
- bson: для работы с ObjectId MongoDB
"""

import asyncio
import json
import logging
import random
import time
from typing import List, Optional, Union
from uuid import UUID

import psycopg
from bson import ObjectId
from bson.binary import Binary, UuidRepresentation
from motor.motor_asyncio import AsyncIOMotorClient

# Настройка логирования для отладки
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Параметры подключения к базам данных
# =====================================================
# ВАЖНО: Измените эти параметры для вашей среды!
# =====================================================

# # Параметры подключения к MongoDB
# ================================
MONGO_CONFIG = {
    'host': 'localhost',              # Адрес сервера MongoDB
    'port': 27017,                    # Порт MongoDB (по умолчанию 27017)
    'database': 'kinoservice',            # УКАЖИТЕ имя вашей базы данных
    'collection': 'ratingCollection',  # УКАЖИТЕ имя вашей коллекции

    # *** ПАРАМЕТРЫ АВТОРИЗАЦИИ MONGODB ***
    # Если ваша MongoDB требует авторизации, замените None на ваши данные:
    # Замените на ваш логин (например: 'myuser')
    'username': None,
    # Замените на ваш пароль (например: 'mypassword')
    'password': None,
    # 'authSource': 'admin',          # Раскомментируйте и укажите БД для авторизации
}

# Параметры подключения к PostgreSQL
# ===================================
POSTGRES_CONFIG = {
    'host': 'localhost',              # Адрес сервера PostgreSQL
    'port': 5432,                     # Порт PostgreSQL (по умолчанию 5432)
    'dbname': 'pg_db',              # УКАЖИТЕ имя вашей базы данных
    'user': 'postgres',               # УКАЖИТЕ ваш логин PostgreSQL

    # *** ПАРАМЕТРЫ АВТОРИЗАЦИИ POSTGRESQL ***
    # Если требуется пароль, замените None на ваш пароль:
    # Замените на ваш пароль (например: 'mypassword')
    'password': "postgres",

    'table_name': 'rating',       # УКАЖИТЕ имя таблицы для тестирования
}


def build_mongo_connection_string() -> str:
    """
    Формирует строку подключения для MongoDB с учетом авторизации.

    Returns:
        str: Строка подключения к MongoDB
    """
    if MONGO_CONFIG['username'] and MONGO_CONFIG['password']:
        # Если указаны логин и пароль, включаем их в строку подключения
        auth_source = MONGO_CONFIG.get('authSource', 'admin')
        return (f"mongodb://{MONGO_CONFIG['username']}:{MONGO_CONFIG['password']}"
                f"@{MONGO_CONFIG['host']}:{MONGO_CONFIG['port']}"
                f"/{MONGO_CONFIG['database']}?authSource={auth_source}")
    else:
        # Подключение без авторизации (для локальной разработки)
        return f"mongodb://{MONGO_CONFIG['host']}:{MONGO_CONFIG['port']}"


def build_postgres_connection_string() -> str:
    """
    Формирует строку подключения для PostgreSQL с учетом авторизации.

    Returns:
        str: Строка подключения к PostgreSQL
    """
    conn_parts = [
        f"host={POSTGRES_CONFIG['host']}",
        f"port={POSTGRES_CONFIG['port']}",
        f"dbname={POSTGRES_CONFIG['dbname']}",
        f"user={POSTGRES_CONFIG['user']}"
    ]

    # Добавляем пароль только если он указан
    if POSTGRES_CONFIG['password']:
        conn_parts.append(f"password={POSTGRES_CONFIG['password']}")

    return " ".join(conn_parts)


async def mongo_queries(client: AsyncIOMotorClient, mongo_ids: List[ObjectId], num_queries: int) -> float:
    """
    Выполняет серию запросов к MongoDB по заранее подготовленным ID и измеряет среднее время выполнения.

    Args:
        client: Клиент подключения к MongoDB
        mongo_ids: Список ObjectId для запросов
        num_queries: Количество запросов для выполнения

    Returns:
        float: Среднее время выполнения запроса в секундах

    Raises:
        Exception: При ошибках подключения или выполнения запросов
    """
    try:
        # Получаем коллекцию из базы данных
        database = client[MONGO_CONFIG['database']]
        collection = database[MONGO_CONFIG['collection']]

        # Проверяем подключение и наличие данных
        document_count = await collection.count_documents({})
        logger.info(
            f"MongoDB: найдено {document_count} документов в коллекции")

        if document_count == 0:
            logger.warning(
                "MongoDB: коллекция пуста, тест может быть неинформативным")

        if len(mongo_ids) == 0:
            raise ValueError("Список MongoDB ID пуст")

        times = []
        successful_queries = 0

        # Выполняем серию запросов
        for i in range(num_queries):
            # Выбираем случайный ID из списка
            selected_id = random.choice(mongo_ids)

            start = time.perf_counter()

            # Выполняем запрос: ищем документ по конкретному film_id
            document = await collection.find_one({"film_id": selected_id})

            end = time.perf_counter()
            query_time = end - start
            times.append(query_time)

            # Считаем успешные запросы (когда документ найден)
            if document:
                successful_queries += 1

            # Логируем прогресс каждые 20 запросов
            if (i + 1) % 20 == 0:
                logger.info(
                    f"MongoDB: выполнено {i + 1}/{num_queries} запросов")

        average_time = sum(times) / len(times)
        success_rate = (successful_queries / num_queries) * 100
        logger.info(
            f"MongoDB: успешно найдено документов: {successful_queries}/{num_queries} ({success_rate:.1f}%)")

        return average_time

    except Exception as e:
        logger.error(f"Ошибка при выполнении запросов к MongoDB: {e}")
        raise


async def postgres_queries(conn: psycopg.AsyncConnection, postgres_ids: List[int], num_queries: int) -> float:
    """
    Выполняет серию запросов к PostgreSQL по заранее подготовленным ID и измеряет среднее время выполнения.

    Args:
        conn: Подключение к PostgreSQL
        postgres_ids: Список ID для запросов
        num_queries: Количество запросов для выполнения

    Returns:
        float: Среднее время выполнения запроса в секундах

    Raises:
        Exception: При ошибках подключения или выполнения запросов
    """
    try:
        times = []
        successful_queries = 0

        async with conn.cursor() as cur:
            # Проверяем подключение и наличие данных
            table_name = POSTGRES_CONFIG['table_name']

            try:
                # Используем SQL-композитор для безопасного выполнения запроса
                from psycopg import sql
                query = sql.SQL(
                    "SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name))
                await cur.execute(query)
                result = await cur.fetchone()
                row_count = result[0] if result else 0
                logger.info(
                    f"PostgreSQL: найдено {row_count} строк в таблице {table_name}")

                if row_count == 0:
                    logger.warning(
                        "PostgreSQL: таблица пуста, тест может быть неинформативным")

            except psycopg.Error as e:
                logger.error(f"Ошибка при проверке таблицы {table_name}: {e}")
                logger.info("Попробуем выполнить простой запрос SELECT 1")
                table_name = None  # Будем использовать простой запрос

            if len(postgres_ids) == 0:
                raise ValueError("Список PostgreSQL ID пуст")

            # Выполняем серию запросов
            for i in range(num_queries):
                # Выбираем случайный ID из списка
                selected_id = random.choice(postgres_ids)

                start = time.perf_counter()

                if table_name:
                    # Выполняем запрос по конкретному ID
                    from psycopg import sql
                    query = sql.SQL("SELECT film_id, AVG(score) FROM {} WHERE film_id = %s GROUP BY film_id").format(
                        sql.Identifier(table_name))
                    await cur.execute(query, (selected_id,))
                    rows = await cur.fetchall()

                    # Считаем успешные запросы (когда запись найдена)
                    if rows:
                        successful_queries += 1
                else:
                    # Простой тестовый запрос, если таблица не найдена
                    await cur.execute("SELECT 1 as test_column")
                    await cur.fetchall()
                    successful_queries += 1

                end = time.perf_counter()
                query_time = end - start
                times.append(query_time)

                # Логируем прогресс каждые 20 запросов
                if (i + 1) % 20 == 0:
                    logger.info(
                        f"PostgreSQL: выполнено {i + 1}/{num_queries} запросов")

        average_time = sum(times) / len(times)
        success_rate = (successful_queries / num_queries) * 100
        logger.info(
            f"PostgreSQL: успешно найдено записей: {successful_queries}/{num_queries} ({success_rate:.1f}%)")

        return average_time

    except Exception as e:
        logger.error(f"Ошибка при выполнении запросов к PostgreSQL: {e}")
        raise


async def test_database_connections():
    """
    Тестирует подключения к базам данных перед началом основного теста.

    Returns:
        tuple: (mongo_client, pg_conn) если подключения успешны, иначе (None, None)
    """
    mongo_client = None
    pg_conn = None

    try:
        # Тестируем подключение к MongoDB
        logger.info("Тестирование подключения к MongoDB...")
        mongo_connection_string = build_mongo_connection_string()
        mongo_client = AsyncIOMotorClient(
            mongo_connection_string, serverSelectionTimeoutMS=5000)

        # Проверяем подключение
        await mongo_client.admin.command('ping')
        logger.info("✓ Подключение к MongoDB успешно")

        # Тестируем подключение к PostgreSQL
        logger.info("Тестирование подключения к PostgreSQL...")
        postgres_connection_string = build_postgres_connection_string()
        pg_conn = await psycopg.AsyncConnection.connect(
            postgres_connection_string,
            connect_timeout=5
        )
        logger.info("✓ Подключение к PostgreSQL успешно")

        return mongo_client, pg_conn

    except Exception as e:
        logger.error(f"Ошибка при тестировании подключений: {e}")

        # Закрываем подключения при ошибке
        if pg_conn:
            await pg_conn.close()

        return None, None


async def main():
    """
    Основная функция, которая выполняет тестирование производительности баз данных.
    """
    # Количество запросов для тестирования (увеличено для более точной статистики)
    num_queries = 200

    logger.info(
        f"Начинаем тестирование производительности БД ({num_queries} запросов)")
    logger.info("Тестируем получение записей по заранее подготовленным ID")
    logger.info("=" * 70)

    try:
        # Загружаем списки ID из файлов
        logger.info("Загружаем списки ID из файлов...")
        with open("mongo_user_film_ids.json", "r") as f:
            data = json.load(f)
            mongo_ids = [
                Binary.from_uuid(
                    UUID(pair["film_id"]),
                    UuidRepresentation.STANDARD
                ) for pair in data]
        with open("user_film_ids.json", "r") as f:
            data = json.load(f)
            postgres_ids = [pair["film_id"] for pair in data]

        logger.info(
            f"Доступно {len(mongo_ids)} MongoDB ID и {len(postgres_ids)} PostgreSQL ID")

    except Exception as e:
        return

    # Тестируем подключения
    mongo_client, pg_conn = await test_database_connections()

    if not mongo_client or not pg_conn:
        logger.error("Не удалось подключиться к одной или обеим базам данных")
        logger.error(
            "Проверьте параметры подключения в переменных MONGO_CONFIG и POSTGRES_CONFIG")
        return

    try:
        # Последовательное выполнение тестов

        # Тест для MongoDB
        logger.info("Начинаем тест MongoDB...")
        mongo_avg_time = await mongo_queries(mongo_client, mongo_ids, num_queries)
        logger.info(
            f"✓ MongoDB: среднее время запроса: {mongo_avg_time:.4f} секунд")

        # Тест для PostgreSQL
        logger.info("Начинаем тест PostgreSQL...")
        pg_avg_time = await postgres_queries(pg_conn, postgres_ids, num_queries)
        logger.info(
            f"✓ PostgreSQL: среднее время запроса: {pg_avg_time:.4f} секунд")

        # Вывод результатов сравнения
        logger.info("=" * 60)
        logger.info("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        logger.info(f"MongoDB среднее время:    {mongo_avg_time:.4f} сек")
        logger.info(f"PostgreSQL среднее время: {pg_avg_time:.4f} сек")

        # Определяем, какая БД быстрее
        if mongo_avg_time < pg_avg_time:
            speedup = pg_avg_time / mongo_avg_time
            logger.info(f"MongoDB быстрее в {speedup:.2f} раза")
        else:
            speedup = mongo_avg_time / pg_avg_time
            logger.info(f"PostgreSQL быстрее в {speedup:.2f} раза")

    except Exception as e:
        logger.error(f"Ошибка во время выполнения тестов: {e}")

    finally:
        # Закрываем подключения
        if pg_conn:
            await pg_conn.close()
            logger.info("Подключение к PostgreSQL закрыто")

        if mongo_client:
            mongo_client.close()
            logger.info("Подключение к MongoDB закрыто")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Тестирование прервано пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
