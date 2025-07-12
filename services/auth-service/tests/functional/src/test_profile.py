from http import HTTPStatus
from typing import Any

import pytest
from faker import Faker
from tests.functional.core.config_log import get_logger
from tests.functional.core.settings import test_conf

logger = get_logger(__name__)


@pytest.mark.asyncio
class TestProfile:

    @staticmethod
    def _get_headers_jwt(jwt_tokens: dict) -> dict:
        access_token = jwt_tokens.get("access_token")
        return {"Authorization": f"Bearer {access_token}"}

    @staticmethod
    async def _fill_database_users(cnt_user: int, create_user) -> list[str]:
        faker = Faker()
        user_ids = []
        for _ in range(cnt_user):
            user = await create_user(
                superuser_flag=False, username=faker.user_name(), email=faker.email()
            )
            user_ids.append(str(user.get("user_id")))
        return user_ids

    async def test_get_profile_user_jwt(self, create_user, make_get_request, redis_test):
        jwt_tokens = await create_user()
        headers = self._get_headers_jwt(jwt_tokens)
        user_id = jwt_tokens.get("user_id")
        key_cache = f"profile:user:{user_id}"

        response_body, status = await make_get_request(
            "/profile",
            headers=headers,
        )
        cache = await redis_test(key=key_cache, cached_data=True)

        assert status == HTTPStatus.OK
        assert (
            response_body.get("user_id") == str(user_id)
            and response_body.get("first_name") == "user"
        )
        assert cache is not None

    @pytest.mark.parametrize(
        "query_data, expected_answer",
        [
            (
                {
                    "test_valid": True,
                    "api_key": test_conf.api_key,
                    "cnt_user": 5,
                },
                {"status": HTTPStatus.OK, "cnt_response_profile": 5},
            ),
            (
                {
                    "test_valid": True,
                    "api_key": test_conf.api_key,
                    "unknow_ids": [
                        "b2f453fb-e12c-42ca-98b5-183f4881c30e",
                        "59cf9199-4d7b-4cc8-a0ff-b86d2c32e214",
                        "730c230f-6eed-44da-8bf9-03d6b3c973e4",
                    ],
                },
                {"status": HTTPStatus.OK, "cnt_response_profile": 0},
            ),
            (
                {
                    "test_valid": False,
                    "api_key": "mega_ultra_kluch_ot_vsego",
                    "cnt_user": 5,
                },
                {
                    "status": HTTPStatus.BAD_REQUEST,
                },
            ),
        ],
        ids=["Test valid", "Test valid null profiles", "Test invalid api key"],
    )
    async def test_get_profiles_users_apikey(
        self,
        create_user,
        make_post_request,
        query_data: dict[str, Any],
        expected_answer: dict[str, Any],
    ):

        user_ids = query_data.get("unknow_ids")
        if not user_ids:
            user_ids = await self._fill_database_users(query_data.get("cnt_user"), create_user)
        headers = {"X-Api-Key": query_data.get("api_key")}

        response_body, status = await make_post_request(
            "/internal/fetch-profiles", headers=headers, data={"user_ids": user_ids}
        )

        if query_data.get("test_valid"):
            assert status == expected_answer.get("status")
            assert len(response_body) == expected_answer.get("cnt_response_profile")
        elif not query_data.get("test_valid"):
            assert status == expected_answer.get("status")

    async def test_fetch_all_users_profiles(
        self,
        create_user,
        make_post_request,
    ):
        headers = {"X-Api-Key": test_conf.api_key}
        await self._fill_database_users(51, create_user)

        response_body, status = await make_post_request(
            "/internal/fetch-all-profiles",
            headers=headers,
            params={"page_size": 25, "page_number": 1},
        )

        assert status == HTTPStatus.OK
        assert len(response_body.get("profiles")) == 25
        assert response_body.get("page_current") == 1
        assert response_body.get("page_size") == 25
        assert response_body.get("page_total") == 3
