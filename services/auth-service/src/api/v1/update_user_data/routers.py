from typing import Annotated
from uuid import UUID

from api.v1.update_user_data.schemas import (
    AssignRoleRequest,
    ChangePasswordRequest,
    ChangeUsernameRequest,
    UserResponse,
    UserRoleResponse,
)
from auth_utils import LibAuthJWT, Permissions, access_permissions_check, auth_dep
from db.postgres import get_session
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from models.models import DictRoles, User, UserCred
from services.user_service import RoleService, UserCredService, UserService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

router = APIRouter()

REQUIRED_PERMISSIONS = {Permissions.ASSIGN_ROLE.value}


@router.post(
    "/change-username",
    description="Меняет имя у пользователя",
    summary="Изменение имени пользователя (RPC-стиль)",
    response_description="Успешное изменение имени пользователя",
)
async def change_username(
    request_body: Annotated[ChangeUsernameRequest, Body(description="Данные для изменения имени")],
    session: Annotated[AsyncSession, Depends(get_session)],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> UserResponse | None:
    """Меняет имя пользователя."""
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    user_id = decrypted_token.get("user_id")
    user = await UserService.find_one_or_none(
        session, User.id == user_id, options=[joinedload(User.user_cred)]
    )
    if not user:
        return None
    user = await UserService.set_username(session, user, request_body.username)
    response = UserService.to_response_body(user)
    return response


@router.post(
    "/change-password",
    description="Меняет пароль пользователя",
    summary="Изменение пароля пользователя (RPC-стиль)",
    response_description="Успешное изменение пароля пользователя",
)
async def change_password(
    request_body: Annotated[ChangePasswordRequest, Body(description="Данные для изменения пароля")],
    session: Annotated[AsyncSession, Depends(get_session)],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> UserResponse | None:
    """Меняет пароль пользователя."""
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    new_password = request_body.password
    repeated_password = request_body.repeat_password
    user_id = decrypted_token.get("user_id")
    if new_password != repeated_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )
    user_cred = await UserCredService.find_one_or_none(
        session, UserCred.user_id == user_id, options=[joinedload(UserCred.user)]
    )
    if not user_cred:
        return None
    user_cred = await UserCredService.set_password(session, user_cred, new_password)
    response = UserCredService.to_response_body(user_cred)
    return response


@router.post(
    "/{user_id}/role",
    description="Задаёт роль пользователю",
    summary=f"Назначение роли пользователю (REST-стиль). Необходимые разрешения:{REQUIRED_PERMISSIONS}",  # noqa: E501
    response_description="Роль успешно назначена пользователю",
)
@access_permissions_check(REQUIRED_PERMISSIONS)
async def assign_role(
    user_id: Annotated[UUID, Path(title="Уникальный идентификатор пользователя")],
    request_body: Annotated[AssignRoleRequest, Body(description="Данные для назначения роли")],
    session: Annotated[AsyncSession, Depends(get_session)],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> UserRoleResponse | None:
    new_role = request_body.role
    user = await UserService.find_one_or_none(
        session, User.id == user_id, options=[joinedload(User.user_cred)]
    )
    if not user:
        return None
    role = await RoleService.find_one_or_none(session, DictRoles.role == new_role)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role does not exist",
        )
    await RoleService.set_role(session, user, new_role)
    response = RoleService.to_response_body(user, new_role)
    return response


@router.delete(
    "/{user_id}/role",
    description="Удаляет роль у пользователя и ставит ANONYMOUS",
    summary=f"Удаление роли пользователя (REST-стиль). Необходимые разрешения:{REQUIRED_PERMISSIONS}",  # noqa: E501
    response_description="Роль пользователя успешно удалена и установлена как ANONYMOUS",
)
@access_permissions_check(REQUIRED_PERMISSIONS)
async def revoke_role(
    user_id: Annotated[UUID, Path(title="Уникальный идентификатор пользователя")],
    session: Annotated[AsyncSession, Depends(get_session)],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> UserRoleResponse | None:
    user = await UserService.find_one_or_none(
        session, User.id == user_id, options=[joinedload(User.user_cred)]
    )
    if not user:
        return None
    role = await RoleService.find_one_or_none(session, DictRoles.role == "ANONYMOUS")
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role does not exist",
        )
    await RoleService.set_role(session, user, "ANONYMOUS")
    response = RoleService.to_response_body(user, "ANONYMOUS")
    return response
