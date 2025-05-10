# import asyncio
import http

# import json
import logging
from enum import StrEnum

import requests
from asgiref.sync import async_to_sync

# from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from auth_utils import auth_dep

# from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

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
        # url = "http://127.0.0.1:8000/auth/api/v1/sessions/login"
        url = "http://auth-api:8000/auth/api/v1/sessions/login"
        try:
            response = requests.post(url, json=payload, timeout=5)
        except requests.RequestException as err:
            # a = 1
            err
            return None

        # ! -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
        # for host in settings.ALLOWED_HOSTS:
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
            data = response.json()
            logger.debug(f"Лог - data: {data}")
            try:
                # authorize = asyncio.run(auth_dep())
                # access_token = asyncio.run(authorize.get_raw_jwt(data['access_token']))
                authorize = async_to_sync(auth_dep)()
                access_token = async_to_sync(authorize.get_raw_jwt)(data["access_token"])
                logger.debug(f"Лог - authorize: {authorize}")
                logger.debug(f"Лог - access_token: {access_token}")
                user = User.objects.select_related("user_cred").get(
                    id=access_token["user_id"],
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
