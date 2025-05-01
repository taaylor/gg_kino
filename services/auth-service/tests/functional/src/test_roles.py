from http import HTTPStatus
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from tests.functional.testdata.model_orm import DictRoles, RolesPermissions
from tests.functional.testdata.model_types import PermissionEnum
from tests.functional.testdata.schemes import Permission, RoleDetailResponse


@pytest.mark.asyncio
class TestRoles:

    @pytest.mark.parametrize(
        "query_data, expected_answer",
        [
            (
                {
                    "path_uuid": "some-role",
                    "role": "some-role",
                    "descriptions": "описание",
                    "permissions": [
                        {"permisson": PermissionEnum.FREE_FILMS.value, "descriptions": "описание"},
                        {"permisson": PermissionEnum.ASSIGN_ROLE.value, "descriptions": "описание"},
                    ],
                    "cached_data": True,
                },
                {
                    "status": HTTPStatus.OK,
                    "err_msg_cache": "Роль ожидалась в кеше",
                },
            ),
            (
                {
                    "path_uuid": "RRRR",
                    "role": "some-role",
                    "descriptions": "описание",
                    "permissions": [
                        {"permisson": PermissionEnum.FREE_FILMS.value, "descriptions": "описание"},
                    ],
                    "cached_data": False,
                },
                {
                    "status": HTTPStatus.BAD_REQUEST,
                    "err_msg_cache": "Роль неожидалась в кеше",
                },
            ),
        ],
        ids=["Test valid role", "Test unknow role"],
    )
    async def test_get_role_detail(
        pg_session: AsyncSession,
        make_get_request,
        redis_test,
        query_data: dict[str, Any],
        expected_answer: dict[str, Any],
    ):
        role_detail = RoleDetailResponse(
            role=query_data.get("role"),
            descriptions=query_data.get("descriptions"),
            permissions=[
                Permission(permission=perm.get("permisson"), descriptions=perm.get("descriptions"))
                for perm in query_data.get("permissions")
            ],
        )

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

        uri = f"/roles/{query_data.get("path_uuid")}"

        body, status = await make_get_request(uri=uri)
        cache_data = await redis_test(key=f"role:{role_detail.role}", cached_data=True)

        assert body == role_detail.model_dump()
        assert status == HTTPStatus.OK
        assert cache_data == role_detail.model_dump()
