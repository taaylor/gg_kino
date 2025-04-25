import json
import logging
from functools import lru_cache
from http import HTTPStatus

from api.v1.role.schemas import Permission, Role, RoleDetail
from core.config import app_config
from db.cache import Cache, get_cache
from db.postgres import get_session
from fastapi import Depends, HTTPException
from models.models import DictRoles, RolesPermissions
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)

CACHE_KEY_ROLE = "role:"
CACHE_KEY_ROLES = "role:all"


class RoleService:

    def __init__(self, session_db: AsyncSession, cache: Cache):
        self.session_db = session_db
        self.cache = cache

    async def _get_model_role_by_pk(self, pk: str) -> DictRoles | None:
        """Возвращает модель DictRoles по pk"""
        stmt = (
            select(DictRoles).where(DictRoles.role == pk).options(joinedload(DictRoles.permissions))
        )

        result = await self.session_db.execute(stmt)
        role = result.unique().scalar_one_or_none()

        return role

    async def get_roles(self) -> list[Role]:
        """Возвращает список всех ролей с базовой информацией"""

        role_cache = await self.cache.get(CACHE_KEY_ROLES)

        if role_cache:
            logger.debug(f"Список ролей получен из кеша: {role_cache}")

            return [Role.model_validate(r) for r in json.loads(role_cache)]

        stmt = select(DictRoles.role, DictRoles.descriptions).order_by(DictRoles.role)
        result = await self.session_db.execute(stmt)
        roles = result.all()

        if not roles:
            return list()

        role_list = [Role(role=r.role, descriptions=r.descriptions) for r in roles]

        json_role = json.dumps([r.model_dump(mode="json") for r in role_list])
        await self.cache.background_set(
            key=CACHE_KEY_ROLES, value=json_role, expire=app_config.cache_expire_in_seconds
        )

        return role_list

    async def get_role(self, pk: str) -> RoleDetail | None:
        """Возвращает детальную информацию о роли с разрешениями"""

        cache_key = CACHE_KEY_ROLE + pk
        role_cache = await self.cache.get(cache_key)
        if role_cache:
            logger.debug(f"Список ролей получен из кеша: {role_cache}")
            return RoleDetail.model_validate_json(role_cache)

        role_model = await self._get_model_role_by_pk(pk=pk)

        if not role_model:
            return None

        role = RoleDetail(
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

    async def create_role(self, request_body: RoleDetail) -> RoleDetail:
        """Возвращает созданную роль в системе"""
        try:
            async with self.session_db.begin():
                role = DictRoles(role=request_body.role, descriptions=request_body.descriptions)
                self.session_db.add(role)

                await self.session_db.flush()

                permissions = [
                    RolesPermissions(
                        role_code=role.role,
                        permission=perm.permission.value,
                        descriptions=perm.descriptions,
                    )
                    for perm in request_body.permissions
                ]

                self.session_db.add_all(permissions)
                await self.session_db.commit()
        except IntegrityError as e:
            await self.session_db.rollback()
            logger.debug(f"Ошибка целостности данных: {e}")
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="Объект уже существует"
            ) from e

        role = RoleDetail(
            role=role.role,
            descriptions=role.descriptions,
            permissions=[
                Permission(permission=p.permission, descriptions=p.descriptions)
                for p in permissions
            ],
        )

        await self.cache.background_set(
            key=CACHE_KEY_ROLE + role.role,
            value=role.model_dump_json(),
            expire=app_config.cache_expire_in_seconds,
        )
        return role

    async def update_role(self, pk: str, request_body: RoleDetail) -> RoleDetail:
        """Обновляет роль, возвращает обновленный объект роли"""
        async with self.session_db.begin():
            role = await self._get_model_role_by_pk(pk=pk)
            if role is None:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST, request_body={"message": "объект не найден"}
                )
            role.descriptions = request_body.descriptions

            new_permissons = [
                RolesPermissions(
                    role=role, permission=p.permission.value, descriptions=p.descriptions
                )
                for p in request_body.permissions
            ]

            role.permissions = new_permissons
            self.session_db.add(role)
            await self.session_db.commit()

        role = RoleDetail(
            role=role.role,
            descriptions=role.descriptions,
            permissions=[
                Permission(permission=p.permission, descriptions=p.descriptions)
                for p in new_permissons
            ],
        )

        key_cache = CACHE_KEY_ROLE + pk

        await self.cache.background_set(
            key=key_cache, value=role.model_dump_json(), expire=app_config.cache_expire_in_seconds
        )

        return role


@lru_cache()
def get_role_service(
    cache: Cache = Depends(get_cache), session_db: AsyncSession = Depends(get_session)
) -> RoleService:
    return RoleService(session_db, cache)
