from http import HTTPStatus

import pytest
from sqlalchemy import select
from tests.functional.testdata.model_orm import User


@pytest.mark.asyncio
class TestUserData:

    URL_PATH = "users"

    def _get_headers(self, jwt_tokens: dict) -> dict:
        access_token = jwt_tokens.get("access_token")
        return {"Authorization": f"Bearer {access_token}"}

    async def test_change_username(self, pg_session, create_user, make_post_request):
        jwt_tokens = await create_user()
        user = (await pg_session.execute(select(User))).scalar_one()

        new_username = "new_user"
        payload = {"id": str(user.id), "username": new_username}
        headers = self._get_headers(jwt_tokens)
        response_body, status = await make_post_request(
            f"/{self.URL_PATH}/change-username",
            data=payload,
            headers=headers,
        )

        assert status == HTTPStatus.OK
        assert response_body["username"] == new_username

    async def test_change_password(self, pg_session, create_user, make_post_request):
        jwt_tokens = await create_user()
        user = (await pg_session.execute(select(User))).scalar_one()

        payload = {
            "id": str(user.id),
            "password": "alskdjfhgalskdjfhg",
            "repeat_password": "alskdjfhgalskdjfhg",
        }
        headers = self._get_headers(jwt_tokens)
        response_body, status = await make_post_request(
            f"/{self.URL_PATH}/change-password", data=payload, headers=headers
        )

        assert status == HTTPStatus.OK
        assert response_body["user_id"] == str(user.id)

    async def test_assign_role(self, pg_session, create_user, make_post_request):
        jwt_tokens = await create_user(superuser_flag=True)

        user = (await pg_session.execute(select(User))).scalar_one()
        payload = {"role": "ADMIN"}
        headers = self._get_headers(jwt_tokens)
        response_body, status = await make_post_request(
            f"/{self.URL_PATH}/{user.id}/role", data=payload, headers=headers
        )

        assert status == HTTPStatus.OK
        assert response_body["user_id"] == str(user.id)
        assert response_body["role"] == "ADMIN"

    async def test_revoke_role(
        self, pg_session, create_user, create_all_roles, make_delete_request
    ):
        jwt_tokens = await create_user(superuser_flag=True)
        user = (await pg_session.execute(select(User))).scalar_one()
        await create_all_roles()

        headers = self._get_headers(jwt_tokens)
        response_body, status = await make_delete_request(
            f"/{self.URL_PATH}/{user.id}/role", headers=headers
        )

        assert status == HTTPStatus.OK
        assert response_body["user_id"] == str(user.id)
        assert response_body["role"] == "ANONYMOUS"
