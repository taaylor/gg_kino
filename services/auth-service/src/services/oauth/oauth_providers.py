import base64
import logging

import aiohttp
from core.oauth_conf import providers_conf
from fastapi import HTTPException, status
from models.logic_models import OAuthUserInfo
from models.models_types import ProvidersEnum

from .oauth_abc import OAuthBaseService

logger = logging.getLogger(__name__)


class YandexOAuthProvider(OAuthBaseService):
    def create_token_request(self, code: str) -> tuple[str, dict, dict]:
        url = providers_conf.yandex.access_token_url
        data = {
            "grant_type": "authorization_code",
            "code": code,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {
                base64.b64encode(
                    f"{providers_conf.yandex.client_id}:{providers_conf.yandex.client_secret}"
                    .encode()
                    ).decode()
            }",
        }
        return url, data, headers

    async def get_user_info(
        self,
        session: aiohttp.ClientSession,
        code: str,
    ) -> OAuthUserInfo:
        url, data, headers = self.create_token_request(code=code)

        async with session.post(url, data=data, headers=headers) as token_response:
            token_data = await token_response.json()

            logger.debug(f"Получены данные авторизации через Yandex: {token_data}")

            if token_response.status != status.HTTP_200_OK:
                error_desc = token_data.get(
                    "error_description",
                    "Описание ошибки отсутствует",
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ошибка при авторизации через Yandex: {error_desc}",
                )

        url_info = providers_conf.yandex.api_base_url
        headers = {"Authorization": f"OAuth {token_data.get("access_token")}"}

        async with session.get(url_info, headers=headers) as info_user:
            user_data = await info_user.json()
            logger.debug(f"Получены данные о пользователе через Yandex: {user_data}")

            if info_user.status != status.HTTP_200_OK:
                error_desc = token_data.get(
                    "error_description",
                    "Описание ошибки отсутствует",
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ошибка при авторизации через Yandex: {error_desc}",
                )

            return OAuthUserInfo(
                social_name=ProvidersEnum.YANDEX.value,
                social_id=user_data.get("id"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                gender=user_data.get("sex").upper(),
            )


active_providers = {ProvidersEnum.YANDEX.value: YandexOAuthProvider()}
