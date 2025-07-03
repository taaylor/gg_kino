import pytest_asyncio
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tests.functional.core.config_log import get_logger
from tests.functional.testdata.model_enum import PermissionEnum
from tests.functional.testdata.model_orm import (
    DictRoles,
    RolesPermissions,
    User,
    UserCred,
    UserProfileSettings,
)
from tests.functional.testdata.schemes import LoginRequest

logger = get_logger(__name__)


@pytest_asyncio.fixture(name="create_user")
def create_user(pg_session: AsyncSession, make_post_request):
    async def inner(
        superuser_flag: bool = False, username: str = "user", email: str = "user@mail.ru"
    ) -> dict[str, str]:
        """Отдает токены авторизации, для запросов в API

        : superuser: bool = False - создается администратор/пользователь сервиса
        """
        pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

        if superuser_flag:
            role_code = "ADMIN"
            permissions = [perm for perm in PermissionEnum]
        else:
            role_code = "UNSUB_USER"
            permissions = [PermissionEnum.FREE_FILMS]

        role_exists = await pg_session.scalar(
            select(DictRoles).where(DictRoles.role == role_code).limit(1)
        )

        if not role_exists:
            role = DictRoles(role=role_code)
            pg_session.add(role)
            await pg_session.flush()

            permission_objects = [
                RolesPermissions(role_code=role.role, permission=perm.value) for perm in permissions
            ]
            pg_session.add_all(permission_objects)
            await pg_session.flush()
        else:
            role = role_exists

        # создаем пользователя
        user = User(
            username=username,
            role_code=role.role,
            first_name="user",
            last_name="user",
            gender="MALE",
        )
        pg_session.add(user)
        await pg_session.flush()

        user_cred = UserCred(
            user_id=user.id,
            email=email,
            password=pwd_context.hash("12345678"),
        )

        user_settings = UserProfileSettings(user_id=user.id, user_timezone="America/New_York")

        pg_session.add_all([user_settings, user_cred])

        await pg_session.commit()

        login, uri = (
            LoginRequest(email=user_cred.email, password="12345678"),
            "/sessions/login",
        )

        body, _ = await make_post_request(uri=uri, data=login.model_dump(mode="json"))

        if not body:
            raise AssertionError(f"Endpoint {uri} вернул невалидный ответ")

        access_token = body.get("access_token")
        refresh_token = body.get("refresh_token")

        logger.info(
            f"Пользователь создан, токены получены access={access_token[:5]}, \
                refresh={refresh_token[:5]}",
        )

        headers = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user.id,
        }

        return headers

    return inner
