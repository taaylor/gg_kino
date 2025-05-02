import logging
from functools import lru_cache

from api.v1.role.schemas import RoleDetailRequest, RoleDetailUpdateRequest
from fastapi import HTTPException, status
from models.models import DictRoles, RolesPermissions
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from utils.decorators import backoff, sqlalchemy_handler_exeptions

logger = logging.getLogger(__name__)


class RoleRepository:

    @backoff()
    @sqlalchemy_handler_exeptions
    async def fetch_role_by_pk(self, session: AsyncSession, pk: str) -> DictRoles | None:
        """Возвращает модель DictRoles по pk"""
        stmt = (
            select(DictRoles).where(DictRoles.role == pk).options(joinedload(DictRoles.permissions))
        )
        result = await session.execute(stmt)
        role = result.unique().scalar_one_or_none()
        return role

    @backoff()
    @sqlalchemy_handler_exeptions
    async def fetch_list_roles(self, session: AsyncSession) -> list[DictRoles]:
        stmt = select(DictRoles.role, DictRoles.descriptions).order_by(DictRoles.role)
        result = await session.execute(stmt)
        roles = result.all()
        return roles

    @backoff()
    @sqlalchemy_handler_exeptions
    async def create_role(self, session: AsyncSession, request_body: RoleDetailRequest):
        role = DictRoles(role=request_body.role, descriptions=request_body.descriptions)
        session.add(role)

        await session.flush()

        permissions = [
            RolesPermissions(
                role_code=role.role,
                permission=perm.permission.value,
                descriptions=perm.descriptions,
            )
            for perm in request_body.permissions
        ]

        session.add_all(permissions)
        await session.commit()
        logger.info(f"Создана роль {role.id}")

    @backoff()
    @sqlalchemy_handler_exeptions
    async def update_role(
        self, session: AsyncSession, request_body: RoleDetailUpdateRequest, pk: str
    ):
        role = await self.fetch_role_by_pk(session=session, pk=pk)
        if role is None:
            logger.debug(f"Роль {pk} не найдена")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Роль не существует"
            )

        await session.execute(delete(RolesPermissions).where(RolesPermissions.role_code == pk))

        role.descriptions = request_body.descriptions

        new_permissions = [
            RolesPermissions(role=role, permission=p.permission.value, descriptions=p.descriptions)
            for p in request_body.permissions
        ]

        role.permissions = new_permissions
        session.add(role)
        await session.commit()
        logger.info(f"Роль {pk} обновила данные")

    @backoff()
    @sqlalchemy_handler_exeptions
    async def destroy_role_by_pk(self, session: AsyncSession, pk: str):
        stmt = delete(DictRoles).where(DictRoles.role == pk)
        await session.execute(stmt)
        logger.info(f"Роль {pk} удалена")


@lru_cache()
def get_role_repository() -> RoleRepository:
    return RoleRepository()
