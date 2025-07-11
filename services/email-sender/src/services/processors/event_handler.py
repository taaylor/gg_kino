import json
import logging
from functools import lru_cache

from aio_pika.abc import AbstractIncomingMessage

# from db.postgres import get_async_session
# from models.enums import EventType
# from models.models import EventSchemaMessage  # , Priority
# from models.models import Template
from models.schemas import EventSchemaMessage
from services.sender_service import SenderSerivce, get_sender_service

# from sqlalchemy import select
# from jinja2 import BaseLoader, Environment, select_autoescape
# from email.message import EmailMessage
# from aiosmtplib import SMTP
# from db.cache import Cache
# from services.template_repository import get_tamplate_repository


logger = logging.getLogger(__name__)
SMTP_HOST = "mailhog"
SMTP_PORT = 1025  # совпадает с docker-compose


class EventHandler:
    """Класс для обработки событий, полученных из очереди сообщений."""

    def __init__(self, service: SenderSerivce) -> None:
        self.service = service

    async def event_handler(self, message: AbstractIncomingMessage) -> None:  # noqa: WPS231
        """
        Обработчик события, который будет вызываться при получении сообщения из очереди.
        :param message: Сообщение, содержащее данные события.
        """
        try:  # noqa: WPS229
            logger.info("начинает выполняться обработка сообщения")
            body = json.loads(message.body.decode())
            validated_body = EventSchemaMessage.model_validate(body)

        except Exception as error:
            logger.error(f"Ошибка при обработке события {message}: {error}")
            return await message.nack(requeue=False)
        success = await self.service.send_email(validated_body)
        if success:
            return await message.ack()
        return await message.nack(requeue=False)

        # template_id = event_data.get("template_id")
        # template = None
        # if event_type == EventType.USER_REGISTERED:
        #     # в зависимости от event_type по разному обрабатываем
        #     # ! нужно сделать проверку в кеше, что event_data.get("id") статус не отправлен
        #     async for session in get_async_session():
        #         template = (await session.execute(select(Template)
        # .where(Template.id == template_id))).scalar_one_or_none()

        # elif event_type == EventType.AUTO_MASS_NOTIFY:
        #     # в зависимости от event_type по разному обрабатываем
        #     pass
        # elif event_type == EventType.MANAGER_MASS_NOTIFY:
        #     # в зависимости от event_type по разному обрабатываем
        #     pass
        # else:
        #     # невалидный event_type
        #     return await message.nack(requeue=False)
        # if template:
        #     logger.info(f"Шаблон найден в БД {template.content},
        # тип данных шаблона {type(template.content)}")
        #     rendered_template = render_template_from_string(
        #         template=template.content, username=event_data.get("username", "unknown")
        #     )
        #     logger.info(f"Отрендеренный шаблон выглядит так {rendered_template}")
        #     logger.info(f"Отправка письма на адрес {event_data.get("email")}")
        #     success = await send_email_via_smtp(  # success - True/False
        #         to=event_data.get("email"),
        #         subject="Спасибо за регистрацию",
        #         html_body=rendered_template,
        #     )
        #     if success:
        #         logger.info(f"Отправка письма на адрес
        # {event_data.get("email")} прошла успешно")
        #         # пишем в кеш, что всё отправилось.
        #         # посылам через httpx запрос в `notification-processor`
        # что всё успешно отправилось
        #         # (или просто посылаем что отправилось в любом случае,
        #         # даже если не успешно, но успешные
        # и неуспешные надо разграничивать и это под вопросом)
        #         return await message.ack()


# @lru_cache
# def get_event_handler() -> EventHandler:
#     return EventHandler(
#         get_sender_service()
#         )
@lru_cache
def get_event_handler(service: SenderSerivce = get_sender_service()) -> EventHandler:
    return EventHandler(service)
