import json

from core.logger_config import get_logger
from kafka import KafkaConsumer

logger = get_logger(__name__)


def extract_from_kafka(consumer: KafkaConsumer, batch_size: int = 1000) -> list[dict]:
    """Извлекает батч сообщений из указанных топиков Kafka.

    :param consumer: KafkaConsumerSingleton
    :param batch_size: Размер батча (по умолчанию 1000).
    :return: Список словарей с данными сообщений.
    """
    messages = []
    try:
        logger.info("Запрос батча сообщений...")
        batch = consumer.poll(timeout_ms=5000, max_records=batch_size)
        logger.info(batch)
        for _, raw_messages in batch.items():
            for msg in raw_messages:
                try:
                    message_data = json.loads(msg.value)
                    messages.append(message_data)
                except json.JSONDecodeError as e:
                    logger.error(f"Ошибка при парсинге JSON в топике {msg.topic}: {e}")
                    continue

        logger.info(messages)
        return messages

    except Exception as e:
        logger.error(f"Ошибка при извлечении данных из Kafka: {e}")
        messages = []
        return messages
