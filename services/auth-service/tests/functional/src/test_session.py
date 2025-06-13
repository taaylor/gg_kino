from http import HTTPStatus

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from tests.functional.testdata.model_enum import GenderEnum, PermissionEnum
from tests.functional.testdata.model_orm import (
    DictRoles,
    RolesPermissions,
    User,
    UserCred,
    UserSession,
)
from tests.functional.testdata.schemes import LoginRequest, RegisterRequest


@pytest.mark.asyncio
class TestSessions:

    async def _create_default_role(self, pg_session: AsyncSession):
        role = DictRoles(role="UNSUB_USER", descriptions="...")
        pg_session.add(role)
        await pg_session.flush()
        permission = RolesPermissions(
            role_code=role.role, permission=PermissionEnum.FREE_FILMS.value, descriptions="..."
        )
        pg_session.add(permission)
        await pg_session.commit()

    async def test_register_user(
        self,
        make_post_request,
        pg_session: AsyncSession,
    ):
        await self._create_default_role(pg_session)
        user_register = RegisterRequest(
            username="test_user",
            email="mail@com",
            gender=GenderEnum.MALE.value,
            password="123456789",
        )

        body, status = await make_post_request(
            uri="/sessions/register", data=user_register.model_dump(mode="json")
        )

        assert status == HTTPStatus.OK
        assert body.get("email") == user_register.email
        assert await pg_session.get(User, body.get("user_id"))
        assert await pg_session.get(UserCred, body.get("user_id"))

    async def test_login_user(self, make_post_request, create_user):
        await create_user(superuser_flag=False)
        request_login = LoginRequest(email="user@mail.ru", password="12345678")

        body, status = await make_post_request(
            uri="/sessions/login", data=request_login.model_dump(mode="json")
        )

        assert status == HTTPStatus.OK
        assert body.get("access_token")
        assert body.get("refresh_token")

    async def test_refresh(self, make_post_request, create_user):
        tokens_auth = await create_user(superuser_flag=False)
        headers = {"Authorization": f'Bearer {tokens_auth.get("refresh_token")}'}

        body, status = await make_post_request(uri="/sessions/refresh", headers=headers)

        assert status == HTTPStatus.OK
        assert body.get("access_token")
        assert body.get("refresh_token")

    async def test_logout(
        self,
        make_post_request,
        create_user,
        pg_session: AsyncSession,
    ):
        tokens_auth = await create_user(superuser_flag=False)
        headers = {"Authorization": f'Bearer {tokens_auth.get("access_token")}'}

        body, status = await make_post_request(uri="/sessions/logout", headers=headers)

        assert status == HTTPStatus.OK
        user_session = await pg_session.get(UserSession, tokens_auth.get("user_id"))
        assert user_session is None

    async def test_logout_all(
        self,
        make_post_request,
        create_user,
        pg_session: AsyncSession,
    ):
        tokens_auth = await create_user(superuser_flag=False)
        request_login = LoginRequest(email="user@mail.ru", password="12345678")
        # cсоздаем множество сессий пользователя
        await make_post_request(uri="/sessions/login", data=request_login.model_dump(mode="json"))
        await make_post_request(uri="/sessions/login", data=request_login.model_dump(mode="json"))
        current, _ = await make_post_request(
            uri="/sessions/login", data=request_login.model_dump(mode="json")
        )
        headers = {"Authorization": f'Bearer {current.get("access_token")}'}

        _, status = await make_post_request(uri="/sessions/logout-all", headers=headers)

        assert status == HTTPStatus.OK
        stmt = select(func.count()).where(UserSession.user_id == tokens_auth.get("user_id"))
        session_count = (await pg_session.execute(stmt)).scalar()
        assert session_count == 1

    async def test_entry_history(
        self,
        make_get_request,
        make_post_request,
        create_user,
    ):
        tokens_auth = await create_user(superuser_flag=False)
        request_login = LoginRequest(email="user@mail.ru", password="12345678")
        # cсоздаем множество сессий пользователя
        await make_post_request(uri="/sessions/login", data=request_login.model_dump(mode="json"))
        await make_post_request(uri="/sessions/login", data=request_login.model_dump(mode="json"))
        headers = {"Authorization": f'Bearer {tokens_auth.get("access_token")}'}

        body, status = await make_get_request(uri="/sessions/entry-history", headers=headers)

        assert status == HTTPStatus.OK
        assert len(body.get("history")) == 2
