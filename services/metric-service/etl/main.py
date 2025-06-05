import time

from config import clickhouse_config, kafka_config
from custom_logging import get_logger
from extract import extract_from_kafka
from kafka_connector import KafkaConsumerSingleton
from load import load_to_clickhouse
from transform import transform_messages

logger = get_logger(__name__)


def main():
    logger.info("Запуск функции ETL (Kafka > ETL > ClickHouse)")
    while True:
        KafkaConsumerSingleton(
            *kafka_config.topics,
            bootstrap_servers=kafka_config.bootstrap_servers,
            group_id=kafka_config.group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda x: x.decode("utf-8"),
            consumer_timeout_ms=5000,
        )
        # Извлекаем батч сообщений из Kafka (до 1000 записей)
        logger.info("Получаем сообщения")
        # messages = extract_from_kafka(batch_size=kafka_config.batch_size)
        messages = extract_from_kafka(
            topics=kafka_config.topics,
            bootstrap_servers=kafka_config.bootstrap_servers,
            group_id=kafka_config.group_id,
            batch_size=kafka_config.batch_size,
        )

        logger.info(f"Прочитано сообщений: {len(messages)}")

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
