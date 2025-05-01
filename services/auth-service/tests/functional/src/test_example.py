from http import HTTPStatus

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from tests.functional.testdata.model_enum import PermissionEnum
from tests.functional.testdata.model_orm import DictRoles, RolesPermissions
from tests.functional.testdata.schemas import Permission, RoleDetail


def test_example():
    assert True


async def test_postgres_example(pg_session):
    role = DictRoles(role="some-role", descriptions="test role")
    pg_session.add(role)
    # pg_session.flush() вместо pg_session.commit()
    # алхимия отправит INSERT’ы в базу, но не зафиксирует их.
    # а в фикстуре pg_session rollback() откатит всё.
    await pg_session.flush()
    assert role.role == "some-role"
    result = await pg_session.execute(
        delete(DictRoles).where(DictRoles.role == "some-role").returning(DictRoles.role)
    )
    assert result.scalar_one() == "some-role"


async def test_postgres_example_else(pg_session: AsyncSession, make_get_request, redis_test):
    # подготовка данных
    role_detail = RoleDetail(
        role="some-role",
        descriptions="test role",
        permissions=[
            Permission(permission=PermissionEnum.FREE_FILMS.value, descriptions="описание")
        ],
    )
    # сохраняем объект в бд
    role = DictRoles(role=role_detail.role, descriptions=role_detail.descriptions)
    pg_session.add(role)
    await pg_session.flush()
    permissions = [
        RolesPermissions(
            role_code=role_detail.role,
            permission=perm.permission,
            descriptions=perm.descriptions,
        )
        for perm in role_detail.permissions
    ]
    pg_session.add_all(permissions)
    await pg_session.commit()
    uri = f"/roles/{role_detail.role}"

    body, status = await make_get_request(uri=uri)
    # cache_data = await redis_test(key=f"role:{role_detail.role}")

    assert body == role_detail.model_dump()
    assert status == HTTPStatus.OK
