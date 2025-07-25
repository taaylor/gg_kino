from typing import Any

import backoff
import httpx
import requests

# from core.config import app_config
from core.logger_config import get_logger
from httpx import HTTPStatusError, RequestError

logger = get_logger(__name__)


class HttpClient:
    """
    Универсальный клиент для выполнения HTTP-запросов.

    Используется для взаимодействия между сервисами.
    """

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
    async def async_post_request(
        self,
        url: str,
        json: dict[str, Any] | list[Any],
        timeout: float = 10,
        **kwargs: Any,
    ) -> dict[str, Any] | list[Any]:
        """
        Выполняет POST-запрос с передачей JSON-данных.

        :param url: Адрес запроса.
        :param json: Данные для отправки в теле запроса.
        :param timeout: Таймаут в секундах.
        :param kwargs: Дополнительные параметры httpx.

        :return: Распарсенный JSON-ответ или пустой список в случае ошибки.
        """
        result = []
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url=url, json=json, timeout=timeout, **kwargs)
                response.raise_for_status()
                result = response.json()
            except HTTPStatusError as e:
                logger.error(f"POST запрос по {url} вернул статус код {e.response.status_code}")
                raise e
            except RequestError as e:
                logger.error(f"POST запрос по {url} получил ошибку: {e!r}")
                raise e
            return result

    def sync_post_request(
        self,
        url: str,
        json: dict[str, Any] | list[Any],
    ):
        payload_response = requests.post(url=url, json=json)
        if payload_response.status_code == 200:
            return payload_response.json()
        return []


def get_http_client() -> HttpClient:
    return HttpClient()
