# import asyncio
import http

# import json
import logging
from enum import StrEnum

import requests
from accounts.utils import decode_jwt_payload

# from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

# from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer


User = get_user_model()
logger = logging.getLogger(__name__)


class Roles(StrEnum):
    ADMIN = "ADMIN"
    SUB_USER = "SUB_USER"
    UNSUB_USER = "UNSUB_USER"
    ANONYMOUS = "ANONYMOUS"


class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        logger.debug(f"Лог - email: {username} password: {password}")
        payload = {"email": username, "password": password}
        # url = "http://auth-api:8000/auth/api/v1/sessions/login"
        url = "http://nginx/auth/api/v1/sessions/login"
        try:
            response = requests.post(url, json=payload, timeout=5)
        except requests.RequestException:
            return None
        #     url = f"http://{host}{settings.AUTH_API_LOGIN_URL}"
        #     logger.debug(f"Лог - url: {url}")
        #     try:
        #         # http://127.0.0.1:8000/auth/api/v1/sessions/login
        #         # response = requests.post(url, data=json.dumps(payload))
        #         response = requests.post(url, json=payload, timeout=5)
        #     except requests.RequestException:
        #         continue
        #     if response.status_code == http.HTTPStatus.OK:
        #         break
        # else:
        #     return None
        # ! -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
        if response.status_code == http.HTTPStatus.OK:
            body_response = response.json()
            logger.debug(f"Лог - body_response: {body_response}")
            try:
                payload = decode_jwt_payload(body_response.get("access_token", ""))
                user = User.objects.select_related("user_cred").get(
                    id=payload.get("user_id", ""),
                    role_code=Roles.ADMIN.value,
                )
            except User.DoesNotExist:
                return None
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

            """

            async def get_raw_jwt(
        self, encoded_token: Optional[str] = None
    ) -> Optional[Dict[str, Union[str, int, bool]]]:
            """
