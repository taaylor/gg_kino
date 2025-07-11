import logging
from functools import lru_cache

from aio_pika.abc import AbstractIncomingMessage
from aiohttp import web
from core.config import app_config

# from utils.ws_connections import connections
from core.template_config import env
from db.postgres import get_async_session
from models.enums import EventType
from models.models import EventSchemaMessage  # , Priority
from models.models import Template
from services.base_service import BaseService
from sqlalchemy import select
from storage.cache import Cache

logger = logging.getLogger(__name__)


def render_template_from_string(template: str, **context) -> str:
    """
    Скомпилировать шаблон из строки и отрендерить его.
    """
    tmpl = env.from_string(template)
    return tmpl.render(**context)


class EventHandler(BaseService):
    """Класс для обработки событий, полученных из очереди сообщений."""

    async def event_handler(self, message: AbstractIncomingMessage) -> None:  # noqa: WPS231
        """
        Обработчик события, который будет вызываться при получении сообщения из очереди.
        :param message: Сообщение, содержащее данные события.
        """
        try:  # noqa: WPS229
            body = message.body.decode()
            event_type = body.get("event_type", "UNKNOWN")
            event_data = body.get("event_data", {})
        except Exception as error:
            logger.error(f"Ошибка при обработке события {message}: {error}")
            return await message.nack(requeue=False)
        if event_type == EventType.USER_REGISTERED:
            # в зависимости от event_type по разному обрабатываем
            # ! нужно сделать проверку в кеше, что event_data.get("id") статус не отправлен
            template_id = event_data.get("template_id")
            template = None
            async for session in get_async_session():
                template = await session.execute(select(Template).where(Template.id == template_id))
            if template:
                rendered_template = render_template_from_string(
                    template=template, username=event_data.get("username", "unknown")
                )
            # template =
            rendered_template
        elif event_type == EventType.AUTO_MASS_NOTIFY:
            # в зависимости от event_type по разному обрабатываем
            pass
        elif event_type == EventType.MANAGER_MASS_NOTIFY:
            # в зависимости от event_type по разному обрабатываем
            pass
        else:
            # невалидный event_type
            pass

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
        key_event_send = self.__class__.key_event_send.format(
            user_id=event.user_id, event_id=event.id
        )

        await user_ws.send_json(event.model_dump(mode="json"))
        logger.debug(f"Отправлено сообщение {event.id} пользователю {event.user_id}")

        await self.cache.background_set(
            key=key_event_send,
            value=event.model_dump_json(include={"id"}),
            expire=app_config.redis.cache_expire_time,
        )
        await message.ack()

    async def _set_cache_fail_event(self, event: EventSchemaMessage) -> None:
        """Метод кладет в кеш не отправленное событие"""

        key_event_not_send = self.__class__.key_event_not_send.format(
            user_id=event.user_id, event_id=event.id
        )
        key_event_fail = self.__class__.key_event_fail.format(
            user_id=event.user_id, event_id=event.id
        )

        await self.cache.background_set(
            key=key_event_not_send,
            value=event.model_dump_json(),
            expire=app_config.redis.cache_expire_time,
        )

        await self.cache.background_set(
            key=key_event_fail,
            value=event.model_dump_json(include={"id"}),
            expire=app_config.redis.cache_expire_time,
        )
        logger.info(
            (
                f"Cобытие {event.id} отправлено временно в кеш "
                f"для пользователя {event.user_id}, так как его соединение не активно."
            )
        )


@lru_cache
def get_event_handler(cache: Cache) -> EventHandler:
    return EventHandler(cache)
