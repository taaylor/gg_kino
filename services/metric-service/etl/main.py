import logging
import sys
import time

from config import clickhouse_config, kafka_config
from extract import extract_from_kafka
from load import load_to_clickhouse
from transform import transform_messages


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


def main():
    logger.info("Запуск функции ETL (Kafka > ETL > ClickHouse)")
    while True:
        # Извлекаем батч сообщений из Kafka (до 1000 записей)
        logger.info("Получаем сообщения")
        messages = extract_from_kafka(
            topics=kafka_config.topics,
            bootstrap_servers=kafka_config.bootstrap_servers,
            group_id=kafka_config.group_id,
            batch_size=kafka_config.batch_size,
        )

        # Если сообщений нет, ждём секунду и повторяем цикл
        if not messages:
            time.sleep(15)
            continue

        # Преобразуем сообщения
        transformed_messages = transform_messages(messages=messages)

        # Загружаем в ClickHouse
        load_to_clickhouse(
            data=transformed_messages,
            host=clickhouse_config.host,
            port=clickhouse_config.port,
            user=clickhouse_config.user,
            password=clickhouse_config.default_password,
            database=clickhouse_config.database,
            table_name_dist=clickhouse_config.table_name_dist,
        )


if __name__ == "__main__":
    logger.info("Запуск ETL (Kafka > ETL > ClickHouse)")
    main()
