import logging
import uuid
from functools import lru_cache

from api.v1.auth.schemas import RegisterRequest
from db.cache import Cache, get_cache
from db.postgres import get_session
from fastapi import Depends
from models.models import (  # DictRoles,; RolesPermissions,; UserSession,; UserSessionsHist
    User,
    UserCred,
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


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

            user_cred = UserCred(
                user_id=user.id, email=user_data.email, password=user_data.password
            )

            self.repository.add(user)
            self.repository.add(user_cred)
            await self.repository.commit()

            logger.info(f"Создан пользователь: {user.id=}, {user.username=}")

        except Exception:
            await self.repository.rollback()
            logger.error(f"Ошибка создания пользователя: {user.id=}, {user.username=}")


class LoginService:
    def __init__(self, repository: AsyncSession):
        self.repository = repository

    pass


class RefreshService:
    def __init__(self, repository: AsyncSession):
        self.repository = repository

    pass


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
