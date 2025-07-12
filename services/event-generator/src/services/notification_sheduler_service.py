import logging
from typing import Any
from uuid import UUID

from core.config import app_config
from models.logic_models import (
    EventType,
    FilmListSchema,
    Priority,
    RecomendedFilmsSchema,
    RegularMassSendingSchemaRequest,
)
from services.connector_repository import ClientRepository

logger = logging.getLogger(__name__)


class FilmSchedulerService:
    """
    Сервис для периодического получения топ‑фильмов и отправки их в notification-processor.

    Используется в Celery-таске для регулярной генерации уведомлений.
    """

    def __init__(self, client_repository: ClientRepository):
        self.client_repository = client_repository

    async def get_films(self, url: str, params: dict[str, str]) -> dict[str, Any] | list[Any]:
        """
        Получает список фильмов из async-api.

        :param url: Базовый URL для GET-запроса.
        :param params: Параметры запроса (сортировка, пагинация и др.).

        :return: Распарсенный JSON-ответ в виде dict или list, или пустой список при ошибке.
        """
        logger.info(f"get_films: начал выполняться, url={url}, params={params}")
        result = await self.client_repository.get_request(
            url=url,
            params=params,
        )
        count = len(result) if isinstance(result, list) else 1
        logger.info(f"get_films: получено {count} записей")
        return result

    def prepare_payload(
        self,
        recommended_films: RecomendedFilmsSchema,
    ) -> RegularMassSendingSchemaRequest:
        return RegularMassSendingSchemaRequest(
            event_data=recommended_films,
            event_type=EventType.AUTO_MASS_NOTIFY,
            method="EMAIL",
            priority=Priority.HIGH,
            source="event-generator",
            # TODO: template_id хардкодом
            template_id=UUID("104c743c-030c-41f9-a714-62392a46e71d"),
        )

    async def send_films_to_notification(
        self, url: str, response_schema: RegularMassSendingSchemaRequest
    ) -> dict[str, Any] | list[Any]:
        """
        Отправляет сформированный payload в notification-processor.

        :param url: Базовый URL для POST-запроса.
        :param response_schema: Данные для отправки (список словарей или словарь).

        :return: Распарсенный JSON-ответ целевого сервиса или пустой список при ошибке.
        """
        count = len(response_schema) if isinstance(response_schema, list) else 1
        logger.info(f"send_films_to_notification: отправка {count} записей на {url}")
        return await self.client_repository.post_request(
            url=url,
            json_data=response_schema.model_dump(mode="json"),
        )

    async def execute_task(self) -> dict[str, Any] | list[Any]:
        """
        Основной рабочий метод: получает фильмы, валидирует и отправляет.

        :return: Ответ от notification-processor или пустой список при неуспехе.
        """
        logger.info("execute_task: начал выполняться")
        json_data = await self.get_films(
            url=app_config.filmapi.get_last_films_url,
            params={"sort": "-imdb_rating", "page_size": "10", "page_number": "1"},
        )
        validated_films = [
            FilmListSchema(
                film_id=film["uuid"],
                film_title=film["title"],
                imdb_rating=film["imdb_rating"],
            )
            for film in json_data
        ]
        recommended_films = RecomendedFilmsSchema(recommended_films=validated_films)
        payload = self.prepare_payload(recommended_films=recommended_films)
        result = await self.send_films_to_notification(
            url=app_config.notification_api.send_to_mass_notification_url,
            response_schema=payload,
        )
        logger.info(f"execute_task: выполнен с результатом {result}")
        return result


def get_film_scheduler_service() -> FilmSchedulerService:
    return FilmSchedulerService(client_repository=ClientRepository())
