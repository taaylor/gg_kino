import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tests.functional.core.config_log import get_logger
from tests.functional.testdata.model_enum import PermissionEnum
from tests.functional.testdata.model_orm import DictRoles, RolesPermissions

logger = get_logger(__name__)


@pytest_asyncio.fixture(name="create_all_roles")
def create_all_roles(pg_session: AsyncSession):
    async def inner() -> None:
        roles_data = {
            "ADMIN": [perm for perm in PermissionEnum],
            "SUB_USER": [
                PermissionEnum.PAID_FILMS,
                PermissionEnum.FREE_FILMS,
            ],
            "UNSUB_USER": [
                PermissionEnum.FREE_FILMS,
            ],
            "ANONYMOUS": [
                PermissionEnum.FREE_FILMS,
            ],
        }
        query = select(DictRoles.role)
        result = await pg_session.execute(query)
        roles = result.scalars().all()
        for role_value in roles_data.keys() - set(roles):
            role = DictRoles(role=role_value)
            pg_session.add(role)
            await pg_session.flush()
            permissions = [
                RolesPermissions(role_code=role.role, permission=perm.value)
                for perm in roles_data[role_value]
            ]
            pg_session.add_all(permissions)
        await pg_session.commit()

    return inner
