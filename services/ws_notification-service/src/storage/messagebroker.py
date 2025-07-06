import logging
from abc import ABC, abstractmethod
from typing import Coroutine

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustChannel, AbstractRobustConnection
from aio_pika.exceptions import AMQPConnectionError
from aio_pika.pool import Pool
from aiohttp import web
from core.config import app_config

logger = logging.getLogger(__name__)


class AsyncMessageBroker(ABC):
    """Абстрактный класс для работы с брокером сообщений."""

    @abstractmethod
    async def consumer(self, queue_name: str, callback: Coroutine):
        """
        Метод позволяет прочитать сообщения из очереди, и выполнить их обработку
        :queue_name - название очереди
        :callback - функция обработки события
        """

    @abstractmethod
    async def close(self):
        """
        Метод позволяет закрыть все активные пулы соединений, каналов с брокером
        """


class RabbitMQConnector(AsyncMessageBroker):
    """Класс для работы с RabbitMQ, использует пул соединений и каналов для асинхронной работы"""

    __slots__ = ("hosts", "_channel_pool", "_connection_pool")

    login = app_config.rabbitmq.user
    password = app_config.rabbitmq.password

    def __init__(self, hosts: list[str]):
        self.hosts = hosts
        self._channel_pool: Pool = Pool(self._get_channel, max_size=2)
        self._connection_pool: Pool = Pool(self._get_connection, max_size=2)

    async def _get_connection(self) -> AbstractRobustConnection:
        for host in self.hosts:
            try:
                connect = await aio_pika.connect_robust(
                    host=host, login=self.__class__.login, password=self.__class__.password
                )
                logger.debug(f"Установлено соединение с нодой {host=}")
                return connect
            except AMQPConnectionError as error:
                logger.error(
                    f"[RabbitMQ] Не удалось установить соединение с нодой {host} : {error=}"
                )
        logger.error("[RabbitMQ] Не удалось подключиться к rabbitmq")
        raise web.HTTPInternalServerError(text="Сервер немножко устал, повторите попытку позже")

    async def _get_channel(self) -> AbstractRobustChannel:
        async with self._connection_pool.acquire() as connection:
            channel = await connection.channel()
            logger.debug(f"Создан канал для соединения с {connection}")
            return channel

    async def consumer(self, queue_name: str, callback: Coroutine):
        async with self._channel_pool.acquire() as channel:
            queue = await channel.declare_queue(queue_name, passive=True)
            logger.debug(f"Подключение к очереди {queue_name} для чтения сообщений")
            async with queue.iterator() as queue_iter:
                logger.debug(f"Начинаем чтение сообщений из очереди {queue_name}")
                message: AbstractIncomingMessage
                async for message in queue_iter:
                    await callback(message)

    async def close(self):
        await self._channel_pool.close()
        await self._connection_pool.close()
        logger.info("Соединение с rabbitmq закрыто")


messagebroker: AsyncMessageBroker | None = None


def get_message_broker() -> AsyncMessageBroker:
    global messagebroker
    if messagebroker is None:
        messagebroker = RabbitMQConnector(hosts=app_config.rabbitmq.hosts)
    return messagebroker
