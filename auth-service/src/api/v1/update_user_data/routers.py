from typing import Annotated
from uuid import UUID

from db.postgres import get_session
from fastapi import APIRouter, Depends, HTTPException, Path, status
from models.models import DictRoles, User, UserCred
from models.models_types import RoleEnum
from schemas.entity import ChangePasswordRequest, ChangeUsernameRequest
from services.user_service import RoleService, UserCredService, UserService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.put("/change-username")
async def change_username(
    request_body: ChangeUsernameRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Меняет имя пользователя."""
    user = await UserService.find_one_or_none(session, User.id == request_body.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )
    user = await UserService.set_username(session, user, request_body.username)
    return {"success": f"Your new username: '{user.username}'."}


@router.put("/change-password")
async def change_password(
    request_body: ChangePasswordRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Меняет пароль пользователя."""
    new_password, repeated_password = request_body.password, request_body.repeat_password
    if new_password != repeated_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )
    user_cred = await UserCredService.find_one_or_none(session, UserCred.user_id == request_body.id)

    if not user_cred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )
    user_cred = await UserCredService.set_password(session, user_cred, new_password)
    return {"success": "Your password changed."}


@router.put("/{user_id}/role")
async def assign_role(
    user_id: Annotated[UUID, Path(title="Уникальный идентификатор пользователя")],
    role: RoleEnum,
    session: AsyncSession = Depends(get_session),
):
    new_role = role.value
    user = await UserService.find_one_or_none(session, User.id == user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )
    role = await RoleService.find_one_or_none(session, DictRoles.role == new_role)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"role {new_role} not found",
        )
    await RoleService.set_role(session, user, new_role)
    return {"success": f"User {user.username} get role {new_role}."}


@router.delete("/{user_id}/role")
async def revoke_role(
    user_id: Annotated[UUID, Path(title="Уникальный идентификатор пользователя")],
    session: AsyncSession = Depends(get_session),
):
    user = await UserService.find_one_or_none(session, User.id == user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )
    await RoleService.set_role(session, user, RoleEnum.ANONYMOUS.value)
    return {"success": f"User role was revoked, and set to {RoleEnum.ANONYMOUS.value}."}
