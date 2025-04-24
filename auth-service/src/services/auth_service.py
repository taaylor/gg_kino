import datetime
import logging
import uuid
from functools import lru_cache

from api.v1.auth.schemas import RegisterRequest, RegisterResponse, Session
from db.cache import Cache, get_cache
from db.postgres import get_session
from fastapi import Depends
from models.models import (  # DictRoles,; RolesPermissions,; UserSession,; UserSessionsHist
    User,
    UserCred,
)
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["argon2"])


class RegisterService:
    def __init__(self, repository: AsyncSession):
        self.repository = repository

    async def create_user(self, user_data: RegisterRequest) -> None:
        try:
            user = User(
                id=uuid.uuid4(),
                username=user_data.username,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                gender=user_data.gender,
                role_code="UNSUB_USER",
            )

            hashed_password = pwd_context.hash(user_data.password)

            user_cred = UserCred(user_id=user.id, email=user_data.email, password=hashed_password)

            self.repository.add(user)
            self.repository.add(user_cred)
            await self.repository.commit()
            logger.info(f"Создан пользователь: {user.id=}, {user.username=}")

            return RegisterResponse(
                user_id=user.id,
                username=user.username,
                email=user_cred.email,
                first_name=user.first_name,
                last_name=user.last_name,
                gender=user.gender,
                session=Session(
                    access_token="access_token",
                    refresh_token="refresh_token",
                    expires_at=datetime.datetime.now(datetime.timezone.utc),
                ),
            )

        except IntegrityError as e:
            await self.repository.rollback()
            logger.error(f"Нарушение консистентности данных: {e}")


class LoginService:
    def __init__(self, repository: AsyncSession):
        self.repository = repository

    pass


class RefreshService:
    def __init__(self, repository: AsyncSession):
        self.repository = repository

    pass


@lru_cache
def get_register_service(repository: AsyncSession = Depends(get_session)) -> RegisterService:
    return RegisterService(repository=repository)


@lru_cache
def get_login_service(repository: AsyncSession = Depends(get_session)) -> RegisterService:
    register_service = RegisterService(repository=repository)
    return register_service


@lru_cache
def get_refresh_service(
    cache: Cache = Depends(get_cache), repository: AsyncSession = Depends(get_session)
) -> RegisterService:
    register_service = RegisterService(repository=repository)
    return register_service
