from typing import Annotated
from uuid import UUID

from db.postgres import get_session
from fastapi import APIRouter, Depends, HTTPException, Path, status
from models.models import DictRoles, User, UserCred
from schemas.entity import AssignRoleRequest, ChangePasswordRequest, ChangeUsernameRequest
from services.user_service import RoleService, UserCredService, UserService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.put(
    "/change-username",
    description="Меняет имя у пользователя",
    # summary="Фильмы с участием персоны",
    # response_description="Список кинопроизведений: UUID, название и рейтинг",
)
async def change_username(
    request_body: ChangeUsernameRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Меняет имя пользователя."""
    user = await UserService.find_one_or_none(session, User.id == request_body.id)
    if not user:
        return None
    user = await UserService.set_username(session, user, request_body.username)
    return {"success": f"Your new username: '{user.username}'."}


@router.put(
    "/change-password",
    description="Меняет пароль пользователя",
    # summary="Фильмы с участием персоны",
    # response_description="Список кинопроизведений: UUID, название и рейтинг",
)
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
        return None
    user_cred = await UserCredService.set_password(session, user_cred, new_password)
    return {"success": "Your password changed."}


@router.put(
    "/{user_id}/role",
    description="Задаёт роль пользователю",
    # summary="Фильмы с участием персоны",
    # response_description="Список кинопроизведений: UUID, название и рейтинг",
)
async def assign_role(
    user_id: Annotated[UUID, Path(title="Уникальный идентификатор пользователя")],
    request_body: AssignRoleRequest,
    session: AsyncSession = Depends(get_session),
):
    new_role = request_body.role
    user = await UserService.find_one_or_none(session, User.id == user_id)
    # можно было бы `if not user or not role:`
    # но сделал так чтобы предотвратить лишний запрос в БД если user не найден
    if not user:
        return None
    role = await RoleService.find_one_or_none(session, DictRoles.role == new_role)
    if not role:
        return None
    await RoleService.set_role(session, user, new_role)
    return {"success": f"User {user.username} get role {new_role}."}


@router.delete(
    "/{user_id}/role",
    description="Удаляет роль у пользователя и ставит ANONYMOUS",
    # summary="Фильмы с участием персоны",
    # response_description="Список кинопроизведений: UUID, название и рейтинг",
)
async def revoke_role(
    user_id: Annotated[UUID, Path(title="Уникальный идентификатор пользователя")],
    session: AsyncSession = Depends(get_session),
):
    user = await UserService.find_one_or_none(session, User.id == user_id)
    if not user:
        return None
    await RoleService.set_role(session, user, "ANONYMOUS")
    return {"success": f"User role was revoked, and set to {'ANONYMOUS'}."}
