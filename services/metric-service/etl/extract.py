import json
import logging

from kafka import KafkaConsumer

# Настройка логирования
logger = logging.getLogger(__name__)


def extract_from_kafka(
    topics: list[str], bootstrap_servers: list[str], group_id: str, batch_size: int = 1000
) -> list[dict]:
    """
    Извлекает батч сообщений из указанных топиков Kafka.

    :param topics: Список топиков Kafka.
    :param bootstrap_servers: Список адресов Kafka-брокеров.
    :param group_id: Идентификатор группы потребителей.
    :param batch_size: Размер батча (по умолчанию 1000).
    :return: Список словарей с данными сообщений.
    """
    try:
        consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda x: x.decode("utf-8"),
        )

        # Получаем батч сообщений
        batch = consumer.poll(timeout_ms=1000, max_records=batch_size)

        # Список для хранения распарсенных сообщений
        messages = []

        for _, raw_messages in batch.items():
            # for topic_partition, raw_messages in batch.items():
            for msg in raw_messages:
                try:
                    # Предполагаем, что сообщение — это JSON-строка
                    message_data = json.loads(msg.value)
                    # Добавляем топик для контекста
                    message_data["topic"] = msg.topic
                    messages.append(message_data)
                except json.JSONDecodeError as e:
                    logger.error(f"Ошибка при парсинге JSON в топике {msg.topic}: {e}")
                    continue

        return messages

    except Exception as e:
        logger.error(f"Ошибка при извлечении данных из Kafka: {e}")
        return []
