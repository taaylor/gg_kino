import json
import logging
from functools import lru_cache

from api.v1.role.schemas import (
    Permission,
    RoleDetailRequest,
    RoleDetailResponse,
    RoleDetailUpdateRequest,
    RoleResponse,
)
from core.config import app_config
from db.cache import Cache, get_cache
from db.postgres import get_session
from fastapi import Depends, HTTPException, status
from services.role_repository import RoleRepository, get_role_repository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

CACHE_KEY_ROLE = "role:"
CACHE_KEY_ROLES = "role:all"


class RoleService:

    def __init__(self, session_db: AsyncSession, cache: Cache, repository: RoleRepository):
        self.session_db = session_db
        self.cache = cache
        self.repository = repository

    async def get_roles(self) -> list[RoleResponse]:
        """Возвращает список всех ролей с базовой информацией"""

        role_cache = await self.cache.get(CACHE_KEY_ROLES)

        if role_cache:
            logger.debug(f"Список ролей получен из кеша: {role_cache}")

            return [RoleResponse.model_validate(r) for r in json.loads(role_cache)]

        roles = await self.repository.fetch_list_roles(session=self.session_db)

        if not roles:
            return []

        role_list = [RoleResponse(role=r.role, descriptions=r.descriptions) for r in roles]

        json_role = json.dumps([r.model_dump(mode="json") for r in role_list])
        await self.cache.background_set(
            key=CACHE_KEY_ROLES, value=json_role, expire=app_config.cache_expire_in_seconds
        )

        return role_list

    async def get_role(self, pk: str) -> RoleDetailResponse | None:
        """Возвращает детальную информацию о роли с разрешениями"""

        cache_key = CACHE_KEY_ROLE + pk
        role_cache = await self.cache.get(cache_key)
        if role_cache:
            logger.debug(f"Роль получена из кеша: {role_cache}")
            return RoleDetailResponse.model_validate_json(role_cache)

        role_model = await self.repository.fetch_role_by_pk(session=self.session_db, pk=pk)

        if not role_model:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="объект не найден")

        role = RoleDetailResponse(
            role=role_model.role,
            descriptions=role_model.descriptions,
            permissions=[
                Permission(permission=perm.permission, descriptions=perm.descriptions)
                for perm in role_model.permissions
            ],
        )

        await self.cache.background_set(
            key=cache_key, value=role.model_dump_json(), expire=app_config.cache_expire_in_seconds
        )
        return role

    async def create_role(self, request_body: RoleDetailRequest) -> RoleDetailResponse:
        """Возвращает созданную роль в системе"""

        await self.repository.create_role(session=self.session_db, request_body=request_body)

        role = RoleDetailResponse(
            role=request_body.role,
            descriptions=request_body.descriptions,
            permissions=[
                Permission(permission=p.permission.value, descriptions=p.descriptions)
                for p in request_body.permissions
            ],
        )

        await self.cache.background_set(
            key=CACHE_KEY_ROLE + request_body.role,
            value=role.model_dump_json(),
            expire=app_config.cache_expire_in_seconds,
        )
        return role

    async def update_role(
        self, pk: str, request_body: RoleDetailUpdateRequest
    ) -> RoleDetailResponse:
        """Обновляет роль, возвращает обновленный объект роли"""

        await self.repository.update_role(session=self.session_db, request_body=request_body, pk=pk)

        role = RoleDetailResponse(
            role=pk,
            descriptions=request_body.descriptions,
            permissions=[
                Permission(permission=p.permission.value, descriptions=p.descriptions)
                for p in request_body.permissions
            ],
        )

        key_cache = CACHE_KEY_ROLE + pk
        await self.cache.background_set(
            key=key_cache, value=role.model_dump_json(), expire=app_config.cache_expire_in_seconds
        )

        return role

    async def destroy_role(self, pk: str) -> None:
        """Удаляет роль по pk"""

        await self.repository.destroy_role_by_pk(session=self.session_db, pk=pk)

        await self.cache.background_destroy(key=CACHE_KEY_ROLE + pk)
        await self.cache.background_destroy(key=CACHE_KEY_ROLES)
        return


@lru_cache()
def get_role_service(
    cache: Cache = Depends(get_cache),
    session_db: AsyncSession = Depends(get_session),
    repository: RoleRepository = Depends(get_role_repository),
) -> RoleService:
    return RoleService(session_db, cache, repository)
