import uuid
from http import HTTPStatus

import pytest
from tests.functional.core.config_log import get_logger
from tests.functional.core.settings import test_conf

logger = get_logger(__name__)


@pytest.mark.asyncio
class TestProfile:
    URL_PATH = "profile"

    @staticmethod
    def _get_headers_jwt(jwt_tokens: dict) -> dict:
        access_token = jwt_tokens.get("access_token")
        return {"Authorization": f"Bearer {access_token}"}

    @staticmethod
    def _get_headers_apikey() -> dict:
        return {
            "X-Api-Key": test_conf.api_key_notifi_service,
            "X-Service-Name": test_conf.api_key_notifi_service_name,
        }

    @staticmethod
    def _get_invalid_apikey_headers() -> dict:
        return {
            "X-Api-Key": "invalid_api_key_123",
            "X-Service-Name": test_conf.api_key_notifi_service_name,
        }

    async def test_get_profile_user_jwt(self, create_user, make_get_request):
        jwt_tokens = await create_user()
        headers = self._get_headers_jwt(jwt_tokens)
        user_id = jwt_tokens.get("user_id")

        response_body, status = await make_get_request(
            f"/{self.__class__.URL_PATH}/{user_id}",
            headers=headers,
        )
        logger.info(response_body)

        assert status == HTTPStatus.OK
        assert (
            response_body.get("user_id") == str(user_id)
            and response_body.get("email") == "user@mail.ru"
            and response_body.get("first_name") == "user"
        )

    async def test_get_profile_user_apikey(self, create_user, make_get_request):
        user_payload = await create_user()
        user_id = user_payload.get("user_id")
        headers = self._get_headers_apikey()

        response_body, status = await make_get_request(
            f"/{self.__class__.URL_PATH}/{user_id}",
            headers=headers,
        )

        assert status == HTTPStatus.OK
        assert (
            response_body.get("user_id") == str(user_id)
            and response_body.get("email") == "user@mail.ru"
            and response_body.get("first_name") == "user"
        )

    async def test_get_profile_forbidden_user_jwt(self, create_user, make_get_request):
        jwt_tokens = await create_user()
        headers = self._get_headers_jwt(jwt_tokens)
        non_existent_user_id = str(uuid.uuid4())

        _, status = await make_get_request(
            f"/{self.__class__.URL_PATH}/{non_existent_user_id}",
            headers=headers,
        )

        assert status == HTTPStatus.FORBIDDEN

    async def test_get_profile_nonexistent_user_apikey(self, make_get_request):
        headers = self._get_headers_apikey()
        non_existent_user_id = str(uuid.uuid4())

        response_body, status = await make_get_request(
            f"/{self.__class__.URL_PATH}/{non_existent_user_id}",
            headers=headers,
        )

        assert status == HTTPStatus.OK
        assert response_body is None

    async def test_get_profile_invalid_apikey(self, create_user, make_get_request):
        user_payload = await create_user()
        user_id = user_payload.get("user_id")
        headers = self._get_invalid_apikey_headers()

        _, status = await make_get_request(
            f"/{self.__class__.URL_PATH}/{user_id}",
            headers=headers,
        )

        assert status == HTTPStatus.BAD_REQUEST
