import logging
from functools import lru_cache

from aio_pika.abc import AbstractIncomingMessage
from aiohttp import ClientConnectionError, web
from core.config import app_config
from models.models import EventSchemaMessage, Priority
from services.base_service import BaseService
from storage.cache import Cache
from utils.ws_connections import connections

logger = logging.getLogger(__name__)


class EventHandlerService(BaseService):
    """Класс для обработки событий, полученных из очереди сообщений."""

    async def event_handler(self, message: AbstractIncomingMessage) -> None:
        """
        Обработчик события, который будет вызываться при получении сообщения из очереди.
        :param message: Сообщение, содержащее данные события.
        """

        try:
            event = EventSchemaMessage.model_validate_json(message.body.decode())
            key_not_send_event = self.__class__.key_cache_not_send_event.format(
                user_id=event.user_id, event_id=event.id
            )
            logger.debug(f"Получено сообщение {event.id} из очереди {message.routing_key}")

            user_ws = connections.get(event.user_id)
            if user_ws and not user_ws.closed:
                return await self._send_message_user(user_ws, message, event)

            await self.cache.background_set(
                key=key_not_send_event,
                value=event.model_dump_json(),
                expire=app_config.cache_expire_time,
            )
            logger.info(
                (
                    f"Cобытие {event.id} отправлено временно в кеш "
                    f"для пользователя {event.user_id}, так как его соединение не активно."
                )
            )
            if event.priority in (Priority.HIGH, Priority.MEDIUM):
                await message.nack(requeue=False)
            await message.ack()
            return await self._send_callback_notify_service(message_id=event.id, status="not_send")
        except Exception as error:
            logger.error(f"Ошибка при обработке события {event}: {error}")
            return await message.nack(requeue=False)

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
        key_cache_event = self.__class__.key_cache_send_event.format(
            user_id=event.user_id, event_id=event.id
        )

        if not await self.cache.get(key_cache_event):
            await user_ws.send_json(event)
            logger.debug(f"Отправлено сообщение {event.id} пользователю {event.user_id}")

            await self.cache.background_set(
                key=key_cache_event, value=event.id, expire=app_config.cache_expire_time
            )
            await message.ack()

        return await self._send_callback_notify_service(message_id=event.id, status="send")

    async def _send_callback_notify_service(self, message_id: str, status: str) -> bool:
        """
        Отправляет уведомление в сервис уведомлений о том, что сообщение было успешно обработано.
        :param message_id: Уникальный идентификатор сообщения.
        """
        return True


@lru_cache
def get_event_handler(cache: Cache) -> EventHandlerService:
    return EventHandlerService(cache)
