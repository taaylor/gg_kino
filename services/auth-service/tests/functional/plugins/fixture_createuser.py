import pytest_asyncio
from passlib.context import CryptContext
from tests.functional.core.config_log import get_logger
from tests.functional.testdata.model_enum import PermissionEnum
from tests.functional.testdata.model_orm import DictRoles, RolesPermissions, User, UserCred
from tests.functional.testdata.schemes import LoginRequest

logger = get_logger(__name__)


@pytest_asyncio.fixture(name="create_user")
def create_user(pg_session, make_post_request):
    async def inner(superuser_flag: bool = False) -> dict[str, str]:
        """
        Отдает сессию клиента, для запросов в API

        : superuser: bool = False - создается администратор/пользователь сервиса
        """
        pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

        if superuser_flag:
            role_user = "ADMIN"
            permissions_user = [perm for perm in PermissionEnum]
        else:
            role_user = "UNSUB_USER"
            permissions_user = [PermissionEnum.FREE_FILMS]

        # создаем роль и права для суперпользователя
        role = DictRoles(role=role_user)
        pg_session.add(role)
        await pg_session.flush()

        permissions = [
            RolesPermissions(role_code=role.role, permission=perm.value)
            for perm in permissions_user
        ]
        pg_session.add_all(permissions)

        # создаем пользователя
        user = User(username="user", role_code=role.role)
        pg_session.add(user)
        await pg_session.flush()
        user_cred = UserCred(
            user_id=user.id, email="user@mail.ru", password=pwd_context.hash("12345678")
        )
        pg_session.add(user_cred)
        await pg_session.commit()

        # делаем запрос на получение access_token токена
        login = LoginRequest(email=user_cred.email, password="12345678")

        body, _ = await make_post_request(uri="/sessions/login", data=login.model_dump(mode="json"))

        access_token = body.get("access_token")
        refresh_token = body.get("refresh_token")

        logger.info(
            f"Пользователь создан, токены получены access={access_token[:5]}, \
                refresh={refresh_token[:5]}"
        )

        headers = {"Authorization": f"Bearer {access_token}", "X-Refresh-Token": refresh_token}

        return headers

    return inner
