import asyncio
import logging

from aiohttp import web
from core.config import app_config
from redis.asyncio import Redis
from storage import cache
from storage.messagebroker import AsyncMessageBroker, get_message_broker
from utils.callback import EventHandler, get_event_handler

logger = logging.getLogger(__name__)


async def setup_cache(app: web.Application):
    """
    Устанавливает соединение с хранилищем кеша при инициализации приложения
    """
    cache.cache_conn = Redis(
        host=app_config.redis.host,
        port=app_config.redis.port,
        db=app_config.redis.db,
        decode_responses=True,
        username=app_config.redis.user,
        password=app_config.redis.password,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_error=False,
        retry_on_timeout=False,
    )
    app.setdefault("cache_conn", cache.cache_conn)
    app.setdefault("cache", cache.get_cache())


async def cleanup_cache(app: web.Application):
    """
    Закрывает соединение с хранилищем кеша при остановке приложения
    """
    cache_conn: Redis = app.get("cache_conn")
    if cache_conn:
        await cache_conn.close()


async def setup_message_broker(app: web.Application):
    """
    Устанавливает соединение с брокером сообщений при инициализации приложения
    """
    event_handler: EventHandler = get_event_handler(app.get("cache"))
    message_broker: AsyncMessageBroker = get_message_broker()

    consumer_task = asyncio.create_task(
        message_broker.consumer(
            queue_name=app_config.rabbitmq.review_like_queue, callback=event_handler.event_handler
        ),
        name="message_broker_consumer",
    )

    logger.info("Consumer запущен")

    app.setdefault("message_broker", message_broker)
    app.setdefault("consumer_task", consumer_task)


async def cleanup_message_broker(app: web.Application):
    """Закрывает соединение с брокером сообщений при остановке приложения"""
    message_broker: AsyncMessageBroker = app.get("message_broker")
    consumer_task: asyncio.Task = app.get("consumer_task")

    if consumer_task:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info("Consumer остановлен")

    if message_broker:
        await message_broker.close()
