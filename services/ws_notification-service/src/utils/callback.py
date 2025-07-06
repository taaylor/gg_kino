import json
import logging
from functools import lru_cache

from aio_pika.abc import AbstractIncomingMessage
from aiohttp import web
from models.models import EventSchemaMessage, Priority
from storage.cache import Cache
from utils.ws_connections import connections

logger = logging.getLogger(__name__)


class EventHandler:
    """Класс для обработки событий, полученных из очереди сообщений."""

    __slots__ = ("cache",)

    key_cache_send_event = "send_event:{user_id}:{event_id}"
    key_cache_not_send_high_event = "not_send_high_event:{user_id}"

    def __init__(self, cache: Cache):
        self.cache = cache

    async def event_handler(self, message: AbstractIncomingMessage) -> None:
        """
        Обработчик события, который будет вызываться при получении сообщения из очереди.
        :param message: Сообщение, содержащее данные события.
        """

        try:
            event = EventSchemaMessage.model_validate_json(message.body.decode())
            user_key_cache_not_send = self.__class__.key_cache_not_send_high_event.format(
                user_id=event.user_id, event_id=event.id
            )

            logger.debug(f"Получено сообщение {event.id} из очереди {message.routing_key}")

            user_ws = connections.get(event.user_id)
            if not user_ws.closed:
                return await self._send_message_user(user_ws, message, event)

            elif event.priority == Priority.HIGH:
                return await self._save_messsage_hight(event, user_key_cache_not_send)

        except Exception as error:
            logger.error(f"Ошибка при обработке события {event}: {error}")
            return await message.nack(requeue=False)

    async def _save_messsage_hight(self, event: EventSchemaMessage, key_cache: str) -> None:
        """
        Сохраняет высокоприоритетное сообщение в кеш, если соединение с пользователем не активно.
        :param event: Данные события.
        """

        if user_event_not_send := await self.cache.get(key_cache):
            user_event_not_send = json.loads(user_event_not_send)
        else:
            user_event_not_send = []

        logger.info(
            (
                f"Высокоприоритетное событие {event.id} отправлено временно в кеш "
                f"для пользователя {event.user_id}, так как его соединение не активно."
            )
        )
        return await self.cache.background_set(
            key=key_cache, value=json.dumps(user_event_not_send.append(event.model_dump)), expire=60
        )

    async def _send_message_user(
        self,
        user_ws: web.WebSocketResponse,
        message: AbstractIncomingMessage,
        event: EventSchemaMessage,
    ) -> None:
        """
        Отправляет сообщение пользователю через WebSocket.
        :param message: Сообщение, содержащее данные события.
        :param event: Данные события, которые будут отправлены пользователю.
        """
        key_cache_event = (
            self.__class__.key_cache_send_event.format(user_id=event.user_id, event_id=event.id),
        )

        if await self.cache.get(key_cache_event):
            logger.debug(
                f"Сообщение {event.id} уже отправлено пользователю {event.user_id}, пропускаем отправку."
            )
        else:
            await user_ws.send_json(event)
            logger.debug(f"Отправлено сообщение {event.id} пользователю {event.user_id}")

            await self.cache.background_set(key=key_cache_event, value=event.id, expire=60)

        if await self._send_callback_notify_service(event.get("id")):
            return await message.ack()
        return await message.nack(requeue=False)

    async def _send_callback_notify_service(self, message_id: str, status: str) -> bool:
        """
        Отправляет уведомление в сервис уведомлений о том, что сообщение было успешно обработано.
        :param message_id: Уникальный идентификатор сообщения.
        """
        return True


@lru_cache
def get_event_handler(cache: Cache) -> EventHandler:
    return EventHandler(cache)
