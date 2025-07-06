import logging

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractRobustConnection
from aio_pika.exceptions import AMQPConnectionError
from core.config import app_config

logger = logging.getLogger(__name__)


nodes = [
    app_config.rabbitmq.get_host(1),
    app_config.rabbitmq.get_host(2),
    app_config.rabbitmq.get_host(3),
]


# Класс для управления продюсером
class AsyncProducer:
    def __init__(self, amqp_urls: list[str]):
        self.amqp_urls = amqp_urls
        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractChannel | None = None

    async def connect(self):  # noqa: WPS231
        for url in self.amqp_urls:
            try:
                self.connection = await aio_pika.connect_robust(url)  # noqa: WPS476
                self.channel = await self.connection.channel()  # noqa: WPS476
                logger.info("Подключение к RabbitMQ установлено")
            except AMQPConnectionError as e:
                logger.error(f"Ошибка подключения к RabbitMQ: {e}")
                raise
            else:
                break

    async def close(self):
        if self.connection:
            await self.connection.close()
            logger.info("Подключение к RabbitMQ закрыто")

    async def publish(self, queue_name: str, message: str):
        if not self.channel:
            raise RuntimeError("Продюсер не подключен")
        # Отправка сообщения в очередь через default exchange
        msg = aio_pika.Message(body=message.encode())
        await self.channel.default_exchange.publish(msg, routing_key=queue_name)
        logger.info(f"Сообщение отправлено в очередь {queue_name}: {message}")


# Глобальный экземпляр продюсера
producer: AsyncProducer | None = None


# Зависимость для получения продюсера
# noqa: WPS231
async def get_producer() -> AsyncProducer:
    global producer  # noqa: WPS420
    if producer is None:
        producer = AsyncProducer(nodes)
        await producer.connect()
    return producer
