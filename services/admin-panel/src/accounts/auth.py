import http
import logging
from enum import StrEnum

import requests
from accounts.utils import decode_jwt_payload
from django.conf import settings
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
        payload = {"email": username, "password": password}
        try:
            response = requests.post(settings.LOGIN_URL, json=payload, timeout=5)
        except requests.RequestException:
            return None
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
