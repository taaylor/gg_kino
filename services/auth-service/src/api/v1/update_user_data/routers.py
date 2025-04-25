from db.postgres import get_session
from fastapi import APIRouter, Depends, HTTPException, status
from models.models import User, UserCred
from schemas.entity import ChangePasswordRequest, ChangeUsernameRequest
from services.user_service import UserCredService, UserService
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
