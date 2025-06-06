import time

from clickhouse_driver import Client
from core.config import clickhouse_config, kafka_config
from core.logger_config import get_logger
from pipeline.extract import extract_from_kafka
from pipeline.load import load_to_clickhouse
from pipeline.transform import transform_messages
from utils.kafka_connector import KafkaConsumerSingleton

logger = get_logger(__name__)


def main():
    kafka_consumer = KafkaConsumerSingleton(
        *kafka_config.topics,
        bootstrap_servers=kafka_config.bootstrap_servers,
        group_id=kafka_config.group_id,
        auto_offset_reset="earliest",
        value_deserializer=lambda x: x.decode("utf-8"),
        consumer_timeout_ms=5000,
        enable_auto_commit=False,
    )
    client_clickhouse = Client(
        host=clickhouse_config.host,
        port=clickhouse_config.port,
        user=clickhouse_config.user,
        password=clickhouse_config.default_password,
    )
    try:
        while True:
            logger.info("Получаем сообщения...")

            messages = extract_from_kafka(
                consumer=kafka_consumer, batch_size=kafka_config.batch_size
            )

            logger.info(f"Прочитано сообщений: {len(messages)}")

            if not messages:
                time.sleep(15)
            else:
                transformed_messages = transform_messages(messages=messages)

                try:
                    load_to_clickhouse(
                        client=client_clickhouse,
                        data=transformed_messages,
                        database=clickhouse_config.database,
                        table_name_dist=clickhouse_config.table_name_dist,
                    )
                    kafka_consumer.commit()
                except Exception as error:
                    logger.error(f"Ошибка записи в ClickHouse: {error}")
                    continue

    except Exception as error:
        logger.error(f"Возникло исключение: {error}")
        kafka_consumer.close()
        client_clickhouse.disconnect()


if __name__ == "__main__":
    logger.info("Запуск ETL (Kafka > ETL > ClickHouse)")
    main()
