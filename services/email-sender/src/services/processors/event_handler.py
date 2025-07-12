import json
import logging
from functools import lru_cache
from typing import Any

import backoff
import httpx
from aio_pika.abc import AbstractIncomingMessage
from core.config import app_config
from httpx import HTTPStatusError, RequestError
from models.schemas import EventSchemaMessage, UpdateStatusSchema
from services.sender_service import SenderSerivce, get_sender_service

logger = logging.getLogger(__name__)


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
            logger.info("Начинает выполняться обработка сообщения")
            body = json.loads(message.body.decode())
            validated_body = EventSchemaMessage.model_validate(body)
            update_status_body = UpdateStatusSchema()

        except Exception as error:
            logger.error(f"Ошибка при обработке события {message}: {error}")
            return await message.nack(requeue=False)
        success = await self.service.send_email(validated_body)
        if success:
            update_status_body.sent_success.append(validated_body.id)
            status_code = self._update_status(
                url=app_config.notificationapi.update_status_url, payload=update_status_body
            )
            logger.info(f"Успех: статус код обновления статуса сообщения: {status_code}")
            return await message.ack()
        update_status_body.failure.append(validated_body.id)
        status_code = self._update_status(
            url=app_config.notificationapi.update_status_url, payload=update_status_body
        )
        logger.error(f"Ошибка: статус код обновления статуса сообщения: {status_code}")
        return await message.nack(requeue=False)

    @backoff.on_exception(
        backoff.expo,
        exception=(
            HTTPStatusError,
            RequestError,
        ),
        max_tries=8,
        raise_on_giveup=False,  # после исчерпанных попыток, не прокидывам исключение дальше
        on_backoff=lambda details: logger.warning(  # логируем на каждой итерации backoff
            (
                f"Повтор {details["tries"]} попытка для"
                f" {details["target"].__name__}. Ошибка: {details["exception"]}"
            )
        ),
        on_giveup=lambda details: logger.error(  # логируем когда попытки исчерпаны
            f"Giveup: функция {details["target"].__name__} исчерпала {details["tries"]} попыток"
        ),
    )
    async def _update_status(
        self,
        url: str,
        payload: UpdateStatusSchema,
        timeout: float = 0.5,
        **kwargs: Any,
    ) -> dict[str, Any] | list[Any]:
        """
        Выполняет POST-запрос с передачей JSON-данных.

        :param url: Адрес запроса.
        :param json_data: Данные для отправки в теле запроса.
        :param timeout: Таймаут в секундах.
        :param kwargs: Дополнительные параметры httpx.

        :return: Распарсенный JSON-ответ или пустой список в случае ошибки.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url=url, json=payload.model_dump(), timeout=timeout, **kwargs
                )
                response.raise_for_status()
            except HTTPStatusError as e:
                logger.error(f"POST запрос по {url} вернул статус код {e.response.status_code}")
                raise e
            except RequestError as e:
                logger.error(f"POST запрос по {url} получил ошибку: {e!r}")
                raise e
            return response.status_code


@lru_cache
def get_event_handler(service: SenderSerivce = get_sender_service()) -> EventHandler:
    return EventHandler(service)
