import logging
from abc import ABC, abstractmethod

import httpx
from core.config import app_config
from models.logic_models import RegisteredNotify
from utils.http_decorators import EmptyServerResponse, handle_http_errors

logger = logging.getLogger(__name__)


class AbstractNotification(ABC):
    """Абстрактный класс для реализации отправки нотификации"""

    @abstractmethod
    async def send_registered_notify(self, notify) -> str:
        """Метод для создания нотификации"""


class NotificationAdapter(AbstractNotification):
    """
    Класс является адаптером для функционала отправки
    нотификации о факте регистрации пользователя.
    """

    @handle_http_errors(service_name=app_config.notifyapi.host)
    async def send_registered_notify(self, notify: RegisteredNotify) -> str:
        """Метод создаёт нотификацию о регистрации пользователя"""
        logger.info(
            f"Получен запрос на отправку нотификации о регистрации пользователя {notify.user_id}"
        )

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(app_config.notifyapi.timeout_sec)
        ) as client:
            data = notify.model_dump(mode="json")
            url = app_config.notifyapi.get_notify_url

            logger.debug(f"Сформирована строка отправки нотификации: {url}")
            logger.debug(f"Сформирована data отправки нотификации: {data}")

            response = await client.post(url=url, json=data)

            response.raise_for_status()

            # Проверяем наличие контента
            if not response.content:
                logger.error(f"Пустой ответ от сервиса {app_config.notifyapi.host}")
                raise EmptyServerResponse("Получен пустой ответ от сервиса фильмов")
            response_json = response.json()
            logger.debug(
                f"Получен ответ от сервиса {app_config.notifyapi.host}: "
                f"идентификатор нотификации: {response_json}"
            )

            return response_json.get("notification_id")


def get_notifier() -> NotificationAdapter:
    return NotificationAdapter()
