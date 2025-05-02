from http import HTTPStatus
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from tests.functional.testdata.model_enum import PermissionEnum
from tests.functional.testdata.model_orm import DictRoles, RolesPermissions
from tests.functional.testdata.schemes import Permission, RoleDetailResponse, RoleResponse


@pytest.mark.asyncio
class TestRoles:

    async def _create_role_in_db(
        self, query_data: dict, pg_session: AsyncSession
    ) -> RoleDetailResponse:
        """Создает роль в БД"""
        role_detail = RoleDetailResponse(
            role=query_data.get("role"),
            descriptions=query_data.get("descriptions"),
            permissions=[
                Permission(permission=perm.get("permission"), descriptions=perm.get("descriptions"))
                for perm in query_data.get("permissions")
            ],
        )

        role = DictRoles(role=role_detail.role, descriptions=role_detail.descriptions)
        pg_session.add(role)
        await pg_session.flush()

        pg_session.add_all(
            [
                RolesPermissions(
                    role_code=role_detail.role,
                    permission=perm.permission,
                    descriptions=perm.descriptions,
                )
                for perm in role_detail.permissions
            ]
        )
        await pg_session.commit()

        return role_detail

    @pytest.mark.parametrize(
        "query_data, expected_answer",
        [
            (
                {
                    "superuser": True,
                    "test": True,  # valid test
                    "path_uuid": "ANONYMOUS",
                    "role": "ANONYMOUS",
                    "descriptions": "описание",
                    "permissions": [
                        {
                            "permission": PermissionEnum.ASSIGN_ROLE.value,
                            "descriptions": "описание",
                        },
                        {"permission": PermissionEnum.FREE_FILMS.value, "descriptions": "описание"},
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
                    "superuser": True,
                    "test": False,  # invalid test
                    "path_uuid": "RRRR",
                    "role": "ANONYMOUS",
                    "descriptions": "описание",
                    "permissions": [
                        {"permission": PermissionEnum.FREE_FILMS.value, "descriptions": "описание"},
                    ],
                    "cached_data": False,
                },
                {
                    "status": HTTPStatus.BAD_REQUEST,
                    "err_msg_cache": "Роль неожидалась в кеше",
                },
            ),
        ],
        ids=[
            "Test valid role",
            "Test invalid role",
        ],
    )
    async def test_get_role_detail(
        self,
        pg_session: AsyncSession,
        make_get_request,
        redis_test,
        query_data: dict[str, Any],
        expected_answer: dict[str, Any],
        create_user,
    ):
        role_detail = await self._create_role_in_db(pg_session=pg_session, query_data=query_data)

        tokens_auth = await create_user(superuser_flag=query_data.get("superuser"))
        headers = {"Authorization": f"Bearer {tokens_auth.get("access_token")}"}
        uri = f"/roles/{query_data.get("path_uuid")}"
        body, status = await make_get_request(uri=uri, headers=headers)
        cache_data = await redis_test(
            key=f"role:{role_detail.role}", cached_data=query_data.get("cached_data")
        )

        assert status == expected_answer.get("status")
        if not query_data.get("test"):
            assert body == {"detail": "объект не найден"}
            assert cache_data is None, expected_answer.get("err_msg_cache")
            return
        assert body == role_detail.model_dump(mode="json")
        assert cache_data == role_detail.model_dump(mode="json"), expected_answer.get(
            "err_msg_cache"
        )

    @pytest.mark.parametrize(
        "query_data, expected_answer",
        [
            (
                {
                    "superuser": True,
                    "roles": [
                        {
                            "role": "ANONYMOUS",
                            "descriptions": "описание",
                            "permissions": [
                                {
                                    "permission": PermissionEnum.ASSIGN_ROLE.value,
                                    "descriptions": "описание",
                                },
                                {
                                    "permission": PermissionEnum.FREE_FILMS.value,
                                    "descriptions": "описание",
                                },
                            ],
                        },
                        {
                            "role": "ROLE",
                            "descriptions": "описание",
                            "permissions": [
                                {
                                    "permission": PermissionEnum.ASSIGN_ROLE.value,
                                    "descriptions": "описание",
                                },
                                {
                                    "permission": PermissionEnum.FREE_FILMS.value,
                                    "descriptions": "описание",
                                },
                            ],
                        },
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
                    "superuser": True,
                    "roles": [
                        {
                            "role": "ROLE",
                            "descriptions": "описание",
                            "permissions": [
                                {
                                    "permission": PermissionEnum.ASSIGN_ROLE.value,
                                    "descriptions": "описание",
                                },
                            ],
                        },
                    ],
                    "cached_data": True,
                },
                {
                    "status": HTTPStatus.OK,
                    "err_msg_cache": "Роль ожидалась в кеше",
                },
            ),
        ],
        ids=["Test valid role list", "Test valid role list"],
    )
    async def test_get_list_role(
        self,
        pg_session: AsyncSession,
        make_get_request,
        redis_test,
        query_data: dict[str, Any],
        expected_answer: dict[str, Any],
        create_user,
    ):

        list_role = []
        for role_data in query_data.get("roles"):
            role = await self._create_role_in_db(query_data=role_data, pg_session=pg_session)
            list_role.append(RoleResponse(role=role.role, descriptions=role.descriptions))

        tokens_auth = await create_user(superuser_flag=query_data.get("superuser"))
        headers = {"Authorization": f"Bearer {tokens_auth.get("access_token")}"}
        body, status = await make_get_request(uri="/roles", headers=headers)
        cache_data = await redis_test(key="role:all", cached_data=query_data.get("cached_data"))

        assert status == expected_answer.get("status")
        body_roles = [r.get("role") for r in body]
        for role in list_role:
            assert role.role in body_roles
            cache_roles = [r.get("role", "") for r in cache_data]
            assert role.role in cache_roles, expected_answer.get("err_msg_cache")
