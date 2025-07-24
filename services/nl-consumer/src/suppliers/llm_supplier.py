import logging

import httpx
from core.config import app_config
from models.logic_models import LlmResponse
from pydantic import ValidationError
from utils.http_decorators import EmptyServerResponse, handle_http_errors

logger = logging.getLogger(__name__)


class LlmSupplier:
    def __init__(self, timeout: int = 120) -> None:
        self.timeout = timeout

    @handle_http_errors(service_name=app_config.llm.host)
    async def execute_nlp(self, genres: set[str], query: str) -> LlmResponse:  # noqa: WPS210
        """Выполняет запрос к LLM для обработки пользовательского запроса."""

        async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:

            prompt = app_config.llm.prompt.format(genres=genres, query=query)

            data = {
                "model": app_config.llm.model,
                "prompt": prompt,
                "stream": False,
                "format": app_config.llm.resp_format,
            }
            headers = {"Content-Type": "application/json"}
            url = app_config.llm.get_url

            logger.debug(f"Сформирована строка запроса: {url}")
            logger.debug(f"Сформирована data запроса: {data}")

            response = await client.post(url=url, json=data, headers=headers)
            response.raise_for_status()
            if not response.content:
                logger.error(f"Пустой ответ от сервиса {app_config.llm.host}")
                raise EmptyServerResponse("Получен пустой ответ от llm")

            try:
                response_data = response.json()
                logger.debug(f"Получен ответ от сервиса {app_config.llm.host}: {response_data}")

                nlp_result = LlmResponse.model_validate_json(response_data["response"])
                return nlp_result
            except ValidationError as e:
                logger.error(f"LLM Ответила с некорректным форматом: {e}")
                return LlmResponse(
                    status="Ошибка при обработке запроса. Пожалуйста, попробуйте ещё раз."
                )


def get_llm_supplier() -> LlmSupplier:
    """Возвращает экземпляр поставщика LLM."""
    return LlmSupplier()
