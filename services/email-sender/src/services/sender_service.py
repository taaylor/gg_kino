# services/email_service.py
import json
import logging
from email.message import EmailMessage
from functools import lru_cache

from aiosmtplib import SMTP
from core.config import app_config
from db.cache import Cache, get_cache
from jinja2 import BaseLoader, Environment, select_autoescape
from models.enums import EventType
from models.schemas import EventSchemaMessage
from services.template_repository import TamplateRepository, get_tamplate_repository

logger = logging.getLogger(__name__)

CACHE_KEY_SEND_EMAIL = "send_email:{user_id}:{event_id}"
CACHE_KEY_FAIL_SEND_EMAIL = "fail_send_email:{user_id}:{event_id}"
CACHE_KEY_INVALID_EVENT_TYPE_SEND_EMAIL = "invalid_event_type_send_email:{user_id}:{event_id}"


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
        self.jinja_env = Environment(
            loader=BaseLoader(),
            autoescape=select_autoescape(["html", "xml"]),
            enable_async=False,
        )

    async def send_email(self, validated_body: EventSchemaMessage) -> bool:
        event_type = validated_body.event_type
        event_data = validated_body.event_data
        user_id = validated_body.user_id
        event_id = validated_body.id
        cache_key_send_email = CACHE_KEY_SEND_EMAIL.format(
            user_id=user_id,
            event_id=event_id,
        )

        logger.info(f"Проверяем статус в кеше по ключу {cache_key_send_email}")
        email_has_been_sent = await self.cache.get(cache_key_send_email)
        logger.info(f"Парсинг сообщения \n event_data: {event_data} \n event_type: {event_type}")
        if not email_has_been_sent:

            logger.info(
                f"Ключ {cache_key_send_email} не найден в кеше, его значение {email_has_been_sent}."
            )
            template = await self.repository.get_tamplate_by_id(event_data.get("template_id"))

            if template:
                logger.info(
                    f"Шаблон найден в БД {template.content}, тип данных {type(template.content)}"
                )
                if event_type == EventType.USER_REGISTERED:
                    context_for_email = {"username": event_data.get("username", "unknown")}
                elif event_type == EventType.AUTO_MASS_NOTIFY:
                    context_for_email = {"username": event_data.get("username", "unknown")}
                elif event_type == EventType.MANAGER_MASS_NOTIFY:
                    context_for_email = {"username": event_data.get("username", "unknown")}
                else:
                    cache_key_invalid_event_type_send_email = (
                        CACHE_KEY_INVALID_EVENT_TYPE_SEND_EMAIL.format(
                            user_id=user_id,
                            event_id=event_id,
                        )
                    )
                    await self.cache.background_set(
                        key=cache_key_invalid_event_type_send_email,
                        value=json.dumps(event_data),
                        expire=app_config.cache_expire_in_seconds_for_email,
                    )
                    return False
                rendered_template = self._render_template_from_string(
                    template=template.content, **context_for_email
                )
                logger.info(f"Отрендеренный шаблон выглядит так {rendered_template}")
                logger.info(f"Отправка письма на адрес {event_data.get("email")}")
                successfully_sent = (
                    await self._send_email_via_smtp(  # successfully_sent - True/False
                        to=event_data.get("email"),
                        subject="Спасибо за регистрацию",
                        html_body=rendered_template,
                    )
                )
                if successfully_sent:
                    logger.info(
                        f"Отправка письма на адрес {event_data.get("email")} прошла успешно"
                    )
                    await self.cache.background_set(
                        key=cache_key_send_email,
                        value=json.dumps(event_data),
                        expire=app_config.cache_expire_in_seconds_for_email,
                    )
                    return True
                cache_key_fail_send_email = CACHE_KEY_FAIL_SEND_EMAIL.format(
                    user_id=user_id,
                    event_id=event_id,
                )
                await self.cache.background_set(
                    key=cache_key_fail_send_email,
                    value=json.dumps(event_data),
                    expire=app_config.cache_expire_in_seconds_for_email,
                )
        return False

    def _render_template_from_string(self, template: str, **context) -> str:
        """
        Скомпилировать шаблон из строки и отрендерить его.
        """
        logger.info(f"Рендеринг шаблона по данным {context}")
        tmpl = self.jinja_env.from_string(template)
        return tmpl.render(**context)

    async def _send_email_via_smtp(self, to: str, subject: str, html_body: str) -> bool:
        logger.info(f"Началась отправка письма на {to}")
        msg = EmailMessage()
        msg["From"] = app_config.smtp.email_yandex_kinoservice
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content("Это HTML письмо. Если оно не отображается проверьте в браузере.")
        msg.add_alternative(html_body, subtype="html")

        smtp = SMTP(hostname=app_config.smtp.smtp_host, port=app_config.smtp.smtp_port)
        await smtp.connect()
        try:
            await smtp.send_message(msg)
            logger.info(f"Успешная отправка письма на {to}")
            return True
        except Exception:
            logger.error(f"Ошибка при отправке письма на {to}")
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
