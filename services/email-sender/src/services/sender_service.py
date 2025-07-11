# services/email_service.py
import logging
from email.message import EmailMessage
from functools import lru_cache

from aiosmtplib import SMTP
from db.cache import Cache, get_cache
from jinja2 import BaseLoader, Environment, select_autoescape
from models.enums import EventType
from models.schemas import EventSchemaMessage
from services.template_repository import TamplateRepository, get_tamplate_repository

logger = logging.getLogger(__name__)

SMTP_HOST = "mailhog"
SMTP_PORT = 1025  # совпадает с docker-compose


def render_template_from_string(template: str, **context) -> str:
    """
    Скомпилировать шаблон из строки и отрендерить его.
    """
    env = Environment(
        loader=BaseLoader(),
        autoescape=select_autoescape(["html", "xml"]),
        enable_async=False,
    )
    logger.info(f"Рендеринг шаблона по данным {context}")
    logger.info(f"Сам шаблон выглядит так {template}")
    tmpl = env.from_string(template)
    logger.info(f"Шаблон выглядит так {tmpl}, тип данных: {type(tmpl)}")
    return tmpl.render(**context)


async def send_email_via_smtp(to: str, subject: str, html_body: str) -> bool:
    msg = EmailMessage()
    msg["From"] = "no-reply@example.com"
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content("This is an HTML email. Please view in HTML client.")
    msg.add_alternative(html_body, subtype="html")

    smtp = SMTP(hostname=SMTP_HOST, port=SMTP_PORT)
    await smtp.connect()
    try:
        await smtp.send_message(msg)
        return True
    except Exception:
        return False
    finally:
        await smtp.quit()


class SenderSerivce:

    def __init__(
        self,
        cache: Cache,
        repository: TamplateRepository,
    ):
        """
        Инициализирует сервис с кешем и репозиторием.

        :param cache: Экземпляр Cache для кеширования результатов.
        :param repository: Репозиторий RatingRepository для работы с БД.
        """
        self.cache = cache
        self.repository = repository

    async def send_email(self, validated_body: EventSchemaMessage) -> bool:
        event_type = validated_body.event_type
        event_data = validated_body.event_data
        logger.info(f"Парсинг сообщения \n event_data: {event_data} \n event_type: {event_type}")
        # ! нужно сделать проверку в кеше, что event_data.get("id") статус не отправлен
        template_id = event_data.get("template_id")
        template = await self.repository.get_tamplate_by_id(template_id)

        if template:
            logger.info(
                f"Шаблон найден в БД {template.content}, тип данных {type(template.content)}"
            )
            if event_type == EventType.USER_REGISTERED:
                context_for_email = {"username": event_data.get("username", "unknown")}
            elif event_type == EventType.AUTO_MASS_NOTIFY:
                # в зависимости от event_type по разному обрабатываем
                context_for_email = {"username": event_data.get("username", "unknown")}
            elif event_type == EventType.MANAGER_MASS_NOTIFY:
                # в зависимости от event_type по разному обрабатываем
                context_for_email = {"username": event_data.get("username", "unknown")}
            else:
                # невалидный event_type
                return False
            rendered_template = self._render_template_from_string(
                template=template.content, **context_for_email
            )
            logger.info(f"Отрендеренный шаблон выглядит так {rendered_template}")
            logger.info(f"Отправка письма на адрес {event_data.get("email")}")
            successfully_sent = await self._send_email_via_smtp(  # successfully_sent - True/False
                to=event_data.get("email"),
                subject="Спасибо за регистрацию",
                html_body=rendered_template,
            )
            if successfully_sent:
                logger.info(f"Отправка письма на адрес {event_data.get("email")} прошла успешно")
                # пишем в кеш, что всё отправилось.
                # посылам через httpx запрос в `notification-processor` что всё успешно отправилось
                # (или просто посылаем что отправилось в любом случае,
                # даже если не успешно,
                # но успешные и неуспешные надо разграничивать и это под вопросом)
                # return await message.ack()
                return True

        return False

    def _render_template_from_string(self, template: str, **context) -> str:
        """
        Скомпилировать шаблон из строки и отрендерить его.
        """
        env = Environment(
            loader=BaseLoader(),
            autoescape=select_autoescape(["html", "xml"]),
            enable_async=False,
        )
        logger.info(f"Рендеринг шаблона по данным {context}")
        logger.info(f"Сам шаблон выглядит так {template}")
        tmpl = env.from_string(template)
        logger.info(f"Шаблон выглядит так {tmpl}, тип данных: {type(tmpl)}")
        return tmpl.render(**context)

    async def _send_email_via_smtp(self, to: str, subject: str, html_body: str) -> bool:
        msg = EmailMessage()
        msg["From"] = "no-reply@example.com"
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content("This is an HTML email. Please view in HTML client.")
        msg.add_alternative(html_body, subtype="html")

        smtp = SMTP(hostname=SMTP_HOST, port=SMTP_PORT)
        await smtp.connect()
        try:
            await smtp.send_message(msg)
            return True
        except Exception:
            return False
        finally:
            await smtp.quit()


@lru_cache
def get_sender_service(
    cache: Cache = get_cache(),
    repository: TamplateRepository = get_tamplate_repository(),
) -> SenderSerivce:
    return SenderSerivce(
        cache=cache,
        repository=repository,
    )
