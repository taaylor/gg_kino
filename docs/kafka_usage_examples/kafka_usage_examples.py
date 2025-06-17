"""Пример использования улучшенного Kafka коннектора"""

from utils.kafka_connector_improved import KafkaConnector, get_kafka_connector


# Пример 1: Использование через контекстный менеджер
def send_user_event(user_id: str, event_type: str, data: dict):
    with KafkaConnector() as kafka:
        message = {
            "user_id": user_id,
            "event_type": event_type,
            "data": data,
            "timestamp": time.time(),
        }

        success = kafka.send_message(
            topic="user_events",
            value=message,
            key=user_id,
            headers={"content-type": b"application/json"},
        )

        if not success:
            # Логика обработки ошибки (например, сохранение в очередь для повторной отправки)
            logger.error("Не удалось отправить событие пользователя %s", user_id)


# Пример 2: Использование глобального экземпляра
def send_metric(metric_name: str, value: float, tags: dict = None):
    kafka = get_kafka_connector()

    message = {
        "metric": metric_name,
        "value": value,
        "tags": tags or {},
        "timestamp": time.time(),
    }

    return kafka.send_message(topic="metrics", value=message, key=metric_name)


# Пример 3: Батчевая отправка
def send_batch_events(events: List[dict]):
    kafka = get_kafka_connector()

    with kafka.producer_context() as producer:
        for event in events:
            try:
                producer.send("events", value=event)
            except Exception as e:
                logger.error("Ошибка отправки события: %s", e)

        # Принудительная отправка всех сообщений
        producer.flush()
