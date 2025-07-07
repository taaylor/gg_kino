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
RABBITMQ_PASS = os.getenv("RABBITMQ_PASSWORD", "pass")
MESSAGE_TTL = int(os.getenv("RABBITMQ_MESSAGE_TTL", "pass"))
DLQ_MESSAGE_TTL = int(os.getenv("RABBITMQ_DLQ_MESSAGE_TTL", "pass"))
DLQ_NAME = os.getenv("RABBITMQ_DLQ_QUEUE")

hosts = ["rabbitmq-1", "rabbitmq-2", "rabbitmq-3"]
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

arguments = {
    "x-queue-type": "quorum",  # Тип очереди — quorum
    "x-quorum-initial-group-size": 3,  # Фактор репликации (3 узла)
    "x-message-ttl": MESSAGE_TTL,  # ttl сообщения в миллисекундах
    "x-delivery-limit": 5,  # количество попыток доставить сообщение до отправки в DLQ
    "x-dead-letter-exchange": "dlx",  # Очередь мёртвых сообщений
    "x-dead-letter-routing-key": "dead.*",  # Шаблон ключа для dlx
}

dlq_arguments = {
    "x-queue-type": "quorum",
    "x-quorum-initial-group-size": 3,
    "x-message-ttl": DLQ_MESSAGE_TTL,
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

        # Объявляем Dead Letter Exchange (DLX) типа "topic"
        channel.exchange_declare(exchange="dlx", exchange_type="topic", durable=True)
        # Объявляем общую Dead Letter Queue (DLQ)
        channel.queue_declare(queue=DLQ_NAME, durable=True, arguments=dlq_arguments)
        # Привязываем DLQ к DLX с шаблоном "dead.*"
        channel.queue_bind(queue="", exchange="dlx", routing_key="dead.*")

        logger.info(f"Список очередей из конфигурации {queues=}")

        for queue in queues:

            queue_arguments = arguments.copy()
            # Для каждой очередь создаю собственный routing-key для DLX по шаблону dead.название_очереди    # noqa: E501
            queue_arguments["x-dead-letter-routing-key"] = f"dead.{queue}"

            channel.queue_declare(queue=queue, durable=True, arguments=queue_arguments)
            logger.info(f"Очередь {queue} создана")
    finally:
        if connection and not connection.is_closed:
            connection.close()
            logger.info("Соединение закрыто")
