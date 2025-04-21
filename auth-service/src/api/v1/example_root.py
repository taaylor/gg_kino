from db.postgres import get_session
from fastapi import APIRouter, Depends
from models.models import User, UserCred
from passlib.hash import argon2

router = APIRouter()


@router.get("/")
async def example_root(session=Depends(get_session)):

    user = User(username="asdasd", first_name="asdasdasd")
    session.add(user)

    user_cred = UserCred(
        user=user,
        password=argon2.hash("12iu3y18whd9u8whe981"),
    )
    session.add(user_cred)
    await session.commit()

    return {"message": "example root"}
