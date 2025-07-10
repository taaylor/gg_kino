import logging
from uuid import UUID

import httpx
from core.config import app_config
from models.logic_models import ProfilePaginate, UserProfile
from pydantic import TypeAdapter
from utils.http_decorators import EmptyServerResponse, handle_http_errors

logger = logging.getLogger(__name__)


class ProfileSupplier:
    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout

    @handle_http_errors(service_name=app_config.profileapi.host)
    async def fetch_profiles(self, user_ids: set[UUID]) -> list[UserProfile]:  # noqa: WPS210
        logger.info(
            f"Получение профилей: {len(user_ids)} "
            f"пользователей от сервиса {app_config.profileapi.host}"
        )

        async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
            headers = {"x-api-key": app_config.profileapi.api_key}
            data = {"user_ids": [str(user_id) for user_id in user_ids]}
            url = app_config.profileapi.get_profile_url

            logger.debug(f"Сформирована строка запроса профиля: {url}")
            logger.debug(f"Сформирована data запроса профиля: {data}")

            response = await client.post(url=url, headers=headers, json=data)
            # Все HTTP ошибки обработает декоратор через raise_for_status()
            response.raise_for_status()

            # Проверяем наличие контента
            if not response.content:
                logger.error(
                    f"Пустой ответ от сервиса {app_config.profileapi.host} "
                    f"для пользователей {user_ids}"
                )
                raise EmptyServerResponse("Получен пустой ответ от сервиса профилей")

            response_data = response.json()

            logger.debug(
                f"Получен ответ от сервиса {app_config.profileapi.host}: "
                f"{len(response_data)} профилей"
            )

            adapter = TypeAdapter(list[UserProfile])
            user_profiles = adapter.validate_python(response_data)

            logger.info(f"Профили: {len(user_profiles)} успешно получены")
            return user_profiles

    @handle_http_errors(service_name=app_config.profileapi.profile_all_path)
    async def fetch_all_profiles(  # noqa: WPS210
        self, page_number: int = 1, page_size: int = 50
    ) -> ProfilePaginate:
        """Получение всех профилей с пагинацией."""

        logger.info(f"Получение всех профилей от сервиса {app_config.profileapi.host}")

        async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
            headers = {"x-api-key": app_config.profileapi.api_key}
            url = app_config.profileapi.profile_all_path
            query_params = {
                "page_number": page_number,
                "page_size": page_size,
            }

            logger.debug(f"Сформирована строка запроса профиля: {url}")

            response = await client.get(url=url, headers=headers, params=query_params)
            response.raise_for_status()

            if not response.content:
                logger.error(
                    f"Пустой ответ от сервиса {app_config.profileapi.host} "
                    "для получения всех профилей c пагинацией"
                )
                raise EmptyServerResponse("Получен пустой ответ от сервиса профилей")

            response_data = response.json()

            logger.debug(
                f"Получен ответ от сервиса {app_config.profileapi.host}: "
                f"{len(response_data.get("profiles", []))} профилей"
            )

            profiles = TypeAdapter(list[UserProfile]).validate_python(
                response_data.get("profiles", [])
            )

            return ProfilePaginate(
                profiles=profiles,
                page_current=response_data.get("page_current", 0),
                page_size=response_data.get("page_size", 0),
                page_total=response_data.get("page_total", 0),
            )


def get_profile_supplier() -> ProfileSupplier:
    return ProfileSupplier()
