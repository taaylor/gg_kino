import logging
from typing import Any

from core.config import app_config
from models.logic_models import FilmListSchemaRequest
from services.connector_repository import ClientRepository

logger = logging.getLogger(__name__)


class FilmSchedulerService:
    """
    Сервис для периодического получения топ‑фильмов и отправки их в notification-processor.

    Используется в Celery-таске для регулярной генерации уведомлений.
    """

    client_repository = ClientRepository()
    # URL_PATH_GET_REQUEST = "http://nginx/async/api/v1/films/"
    URL_PATH_GET_REQUEST = app_config.filmapi.get_last_films_url
    URL_PATH_POST_REQUEST = "http://nginx/notification-api/api/v1/notifications/mock-get-films"

    @classmethod
    async def get_films(cls, url: str, params: dict[str, str]) -> dict[str, Any] | list[Any]:
        """
        Получает список фильмов из async-api.

        :param url: Базовый URL для GET-запроса.
        :param params: Параметры запроса (сортировка, пагинация и др.).

        :return: Распарсенный JSON-ответ в виде dict или list, или пустой список при ошибке.
        """
        logger.info(f"get_films: начал выполняться, url={url}, params={params}")
        result = await cls.client_repository.get_request(
            url=url,
            params=params,
        )
        count = len(result) if isinstance(result, list) else 1
        logger.info(f"get_films: получено {count} записей")
        return result

    @classmethod
    def validate_films(cls, films_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Валидирует и формирует payload для отправки.

        :param films_list: Сырые данные фильмов из API.

        :return: Список словарей с единственным полем film_id для каждого валидного фильма.
        """
        logger.info(f"Валидация фильмов: start, items={len(films_list)}")
        return [FilmListSchemaRequest(film_id=film["uuid"]).model_dump() for film in films_list]

    @classmethod
    async def send_films_to_notification(
        cls, url: str, json_data: list[Any] | dict[str | Any]
    ) -> dict[str, Any] | list[Any]:
        """
        Отправляет сформированный payload в notification-processor.

        :param url: Базовый URL для POST-запроса.
        :param json_data: Данные для отправки (список словарей или словарь).

        :return: Распарсенный JSON-ответ целевого сервиса или пустой список при ошибке.
        """
        count = len(json_data) if isinstance(json_data, list) else 1
        logger.info(f"send_films_to_notification: отправка {count} записей на {url}")
        return await cls.client_repository.post_request(
            url=url,
            json_data=json_data,
        )

    @classmethod
    async def execute_task(cls) -> dict[str, Any] | list[Any]:
        """
        Основной рабочий метод: получает фильмы, валидирует и отправляет.

        :return: Ответ от notification-processor или пустой список при неуспехе.
        """
        logger.info("execute_task: начал выполняться")
        json_data = await cls.get_films(
            url=cls.URL_PATH_GET_REQUEST,
            params={"sort": "-imdb_rating", "page_size": "10", "page_number": "1"},
        )
        validated_films = cls.validate_films(
            data=json_data,
        )
        result = await cls.send_films_to_notification(
            url=cls.URL_PATH_POST_REQUEST,
            json_data=validated_films,
        )
        logger.info(f"execute_task: выполнен с результатом {result}")
        return result
