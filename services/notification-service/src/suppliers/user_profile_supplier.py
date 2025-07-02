import logging
from uuid import UUID

import httpx
from core.config import app_config
from models.logic_models import UserProfile
from utils.http_decorators import EmptyServerResponse, handle_http_errors

logger = logging.getLogger(__name__)


class ProfileSupplier:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    @handle_http_errors(service_name=app_config.profile_api.host)
    async def fetch_profile(self, user_id: UUID) -> UserProfile:  # noqa: WPS210
        logger.info(
            f"Получение профиля пользователя: {user_id} от сервиса {app_config.profile_api.host}"
        )

        async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
            headers = {
                "x-api-key": app_config.profile_api.api_key,
                "x-service-name": app_config.profile_api.service_name,
            }
            url = app_config.profile_api.get_profile_url.format(user_id=user_id)

            logger.debug(f"Сформирована строка запроса профиля: {url}")

            response = await client.get(url=url, headers=headers)
            # Все HTTP ошибки обработает декоратор через raise_for_status()
            response.raise_for_status()

            # Проверяем наличие контента
            if not response.content:
                logger.error(f"Пустой ответ от сервиса профилей для пользователя {user_id}")
                raise EmptyServerResponse("Получен пустой ответ от сервиса профилей")

            # Валидируем JSON и данные через Pydantic
            response_data = response.json()

            logger.info(f"Получен ответ от сервиса профилей: {response_data}")

            user_profile = UserProfile.model_validate(response_data)

            logger.info(f"Профиль пользователя {user_id} успешно получен")
            return user_profile


def get_profile_supplier() -> ProfileSupplier:
    return ProfileSupplier()
