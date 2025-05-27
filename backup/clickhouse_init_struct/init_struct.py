import logging
import os
import sys

from clickhouse_driver import Client, errors
from dotenv import find_dotenv, load_dotenv


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.hasHandlers():
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger


logger = get_logger(__name__)


load_dotenv(find_dotenv())

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST")


def main():
    client = Client(CLICKHOUSE_HOST)

    # Создание базы данных
    client.execute(
        """
        CREATE DATABASE IF NOT EXISTS kinoservice
        ON CLUSTER kinoservice_cluster
    """
    )

    # Создание локальной таблицы с репликацией
    client.execute(
        """
        CREATE TABLE IF NOT EXISTS kinoservice.metrics
        ON CLUSTER kinoservice_cluster
        (
            id Int64,
            user_uuid Nullable(UUID),
            film_uuid Nullable(UUID),
            film_title Nullable(String),
            ip_address Nullable(String),
            event_type String,
            message_event String,
            event_timestamp DateTime,
            user_timestamp DateTime
        )
        ENGINE = ReplicatedMergeTree(
            '/clickhouse/tables/{cluster}/{shard}/metrics',
            '{replica}'
        )
        PARTITION BY toYYYYMMDD(event_timestamp)
        ORDER BY (event_timestamp, id)
    """
    )

    # Создание дистрибутивной таблицы
    client.execute(
        """
        CREATE TABLE IF NOT EXISTS kinoservice.metrics_distributed
        ON CLUSTER kinoservice_cluster
        (
            id Int64,
            user_uuid Nullable(UUID),
            film_uuid Nullable(UUID),
            film_title Nullable(String),
            ip_address Nullable(String),
            event_type String,
            message_event String,
            event_timestamp DateTime,
            user_timestamp DateTime
        )
        ENGINE = Distributed(
            'kinoservice_cluster',
            'kinoservice',
            'metrics',
            rand()
        )
    """
    )


if __name__ == "__main__":
    try:
        main()
        logger.info("Dump базы данных выполнен успешно!")
    except errors.Error as error:
        logger.error(f"Возникло исключение: {error}")
