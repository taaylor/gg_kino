import logging
import os

import pika
from pika.exceptions import AMQPConnectionError
from queue_list import queues

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Получение настроек из переменных окружения
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "pass")

hosts = ["rabbitmq-1", "rabbitmq-2", "rabbitmq-3"]
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

arguments = {
    "x-queue-type": "quorum",  # Тип очереди — quorum
    "x-quorum-initial-group-size": 3,  # Фактор репликации (3 узла)
}


def create_connection():
    parameters = [
        pika.ConnectionParameters(
            host=host,
            credentials=credentials,
            connection_attempts=3,
            retry_delay=5,
        )
        for host in hosts
    ]

    try:
        logger.info(f"Попытка подключения к RabbitMQ кластеру: {hosts}")
        connection = pika.BlockingConnection(parameters)
        logger.info("Подключение успешно установлено!")
        return connection
    except AMQPConnectionError as e:
        logger.error(f"Ошибка подключения к RabbitMQ: {e}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        raise


if __name__ == "__main__":
    connection = None
    try:
        connection = create_connection()
        channel = connection.channel()

        logger.info(f"Список очередей из конфигурации {queues=}")

        for queue in queues:
            channel.queue_declare(queue=queue, durable=True, arguments=arguments)
            logger.info(f"Очередь {queue} создана")
    finally:
        if connection and not connection.is_closed:
            connection.close()
            logger.info("Соединение закрыто")
