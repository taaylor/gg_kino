import json

from custom_logging import get_logger
from kafka_connector import KafkaConsumerSingleton

logger = get_logger(__name__)


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
        logger.info(f"Создание KafkaConsumer для топиков: {topics}")
        logger.info(f"Bootstrap servers: {bootstrap_servers}")
        logger.info(f"Group ID: {group_id}")
        consumer = KafkaConsumerSingleton().consumer
        # consumer = KafkaConsumer(
        #     *topics,
        #     bootstrap_servers=bootstrap_servers,
        #     group_id=group_id,
        #     auto_offset_reset="earliest",  # Читаем с начала для обработки всех сообщений
        #     enable_auto_commit=True,
        #     value_deserializer=lambda x: x.decode("utf-8"),
        #     consumer_timeout_ms=5000,  # Увеличиваем общий timeout
        # )

        logger.info("KafkaConsumer создан успешно")

        # Дожидаемся назначения партиций (важно!)
        logger.info("Ожидание назначения партиций...")
        max_retries = 10
        for i in range(max_retries):
            if consumer.assignment():
                logger.info(f"Партиции назначены: {consumer.assignment()}")
                break
            logger.info(f"Попытка {i+1}/{max_retries}: партиции еще не назначены, ждем...")
            # Вызов poll с timeout=0 триггерит процесс назначения партиций
            consumer.poll(timeout_ms=0)
            import time

            time.sleep(1)
        else:
            logger.warning("Партиции не были назначены после ожидания")

        # Получаем батч сообщений
        logger.info("Запрос батча сообщений...")
        batch = consumer.poll(timeout_ms=5000, max_records=batch_size)  # Увеличиваем timeout

        # Список для хранения распарсенных сообщений
        messages = []

        for _, raw_messages in batch.items():
            # for topic_partition, raw_messages in batch.items():
            for msg in raw_messages:
                try:
                    # Предполагаем, что сообщение — это JSON-строка
                    message_data = json.loads(msg.value)
                    # Добавляем топик для контекста
                    # message_data["topic"] = msg.topic
                    messages.append(message_data)
                except json.JSONDecodeError as e:
                    logger.error(f"Ошибка при парсинге JSON в топике {msg.topic}: {e}")
                    continue

        return messages

    except Exception as e:
        logger.error(f"Ошибка при извлечении данных из Kafka: {e}")
        return []
