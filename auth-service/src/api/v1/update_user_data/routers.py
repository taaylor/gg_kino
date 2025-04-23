from db.postgres import get_session
from fastapi import APIRouter, Depends, HTTPException, status
from models.models import User, UserCred
from passlib.hash import argon2
from schemas.entity import ChangePasswordRequest, ChangeUsernameRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter()


@router.put("/change-username")
async def change_username(
    request_body: ChangeUsernameRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    query = select(User).where(User.id == request_body.id)
    exequted_query = await session.execute(query)
    user = exequted_query.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )

    user.username = request_body.username
    await session.commit()
    return {"success": f"Your new username: '{user.username}'."}


@router.put("/change-password")
async def change_password(
    request_body: ChangePasswordRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    query = select(UserCred).where(UserCred.user_id == request_body.id)
    result = await session.execute(query)
    user_cred = result.scalar_one_or_none()

    if not user_cred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )

    user_cred.password = argon2.hash(request_body.password)
    await session.commit()
    return {"success": "Your password changed."}
