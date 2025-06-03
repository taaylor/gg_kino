from config import clickhouse_config, kafka_config
from extract import extract_from_kafka
from load import load_to_clickhouse
from transform import transform_messages


def main():
    while True:
        # Извлекаем батч сообщений из Kafka (до 1000 записей)
        messages = extract_from_kafka(
            topics=kafka_config.topics,
            bootstrap_servers=kafka_config.bootstrap_servers,
            group_id=kafka_config.group_id,
            batch_size=kafka_config.batch_size,
        )

        # Если сообщений нет, ждём секунду и повторяем цикл
        # if not messages:
        #     time.sleep(1)
        #     continue

        # Преобразуем сообщения
        transformed_messages = transform_messages(messages=messages)

        # Загружаем в ClickHouse
        load_to_clickhouse(
            data=transformed_messages,
            host=clickhouse_config.host,
            port=clickhouse_config.port,
            db_name=clickhouse_config.db_name,
            table_name_dist=clickhouse_config.table_name_dist,
        )


if __name__ == "__main__":
    main()
