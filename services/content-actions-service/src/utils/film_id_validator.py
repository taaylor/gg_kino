import logging
from functools import lru_cache
from uuid import UUID

import aiohttp
from core.config import app_config
from fastapi import HTTPException, status
from ujson import dumps as ujson_dumps  # type: ignore

logger = logging.getLogger(__name__)


class FilmIdValidator:
    """Класс проверяет существует ли запрошенный film_id в базе фильмов сервиса"""

    timeout = aiohttp.ClientTimeout(total=app_config.default_http_timeout)

    async def validate_film_id(self, film_id: UUID) -> bool:  # noqa: WPS210, WPS220
        logger.debug(f"Фильм: {film_id=} будет проверен на наличие в БД фильмов")

        # Для тестирования есть вайтлист uuid, которые считаются валидными, без запроса в async-api
        if film_id in app_config.test_films:
            logger.debug(f"Фильм: {film_id=} в вайтлисте тестовых film_id")
            return True

        async with aiohttp.ClientSession(
            raise_for_status=False, json_serialize=ujson_dumps, timeout=self.timeout
        ) as session:

            request_url = app_config.film_validation_url.format(film_id=film_id)

            logger.debug(f"url для проверки наличия фильма сформирован: {request_url}")

            async with session.get(request_url) as response:
                if not response.ok:
                    response_body = await response.text()
                    logger.error(
                        f"Получена ошибка: {response.status} при проверке наличия фильма: {response_body}"  # noqa: E501
                    )

                response_dict = await response.json(encoding="utf-8")
                if response_dict is not None and (
                    film_title := response_dict.get("title")  # noqa: WPS332
                ):
                    logger.debug(
                        f"Результат проверки фильма {film_id}: Фильм существует '{film_title}'"
                    )
                    return True

                logger.warning(f"Была запрошена валидация: {film_id=}, но фильм не существует")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Указанный идентификатор фильма не существует",
                )


@lru_cache()
def get_film_id_validator():
    return FilmIdValidator()
