from api.v1.update_user_data.schemas import UserResponse, UserRoleResponse
from models.models import DictRoles, User, UserCred
from passlib.hash import argon2
from sqlalchemy.ext.asyncio import AsyncSession
from utils.decorators import sqlalchemy_universal_decorator

from services.base_service import BaseService


class UserService(BaseService):
    """Бизнес-логика для работы с моделью User."""

    model = User

    @classmethod
    @sqlalchemy_universal_decorator
    async def set_username(
        cls,
        session: AsyncSession,
        user: User,
        new_username: str,
    ) -> User:
        """Устанавливает новое имя пользователя и сохраняет изменения в базе данных.

        Аргументы должны передаваться позиционно:
        - session: Асинхронная сессия SQLAlchemy.
        - user: Объект пользователя, чьё имя нужно изменить.
        - new_username: Новое имя пользователя.
        """
        user.username = new_username
        await session.commit()
        return user

    @classmethod
    def to_response_body(cls, user: User) -> None:
        return UserResponse(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            gender=user.gender,
            email=user.user_cred.email,
        )


class UserCredService(BaseService):
    model = UserCred

    @classmethod
    @sqlalchemy_universal_decorator
    async def set_password(
        cls,
        session: AsyncSession,
        user_cred: UserCred,
        new_password: str,
    ) -> UserCred:
        """Устанавливает новый пароль для пользователя и сохраняет изменения в базе данных.

        Аргументы должны передаваться позиционно:
        - session: Асинхронная сессия SQLAlchemy.
        - user_cred: Объект пользователя, чьё имя нужно изменить.
        - new_password: Новый пароль пользователя.
        """
        user_cred.password = argon2.hash(new_password)
        await session.commit()
        return user_cred

    @classmethod
    def to_response_body(cls, user_cred: UserCred) -> None:
        return UserResponse(
            user_id=user_cred.user_id,
            username=user_cred.user.username,
            first_name=user_cred.user.first_name,
            last_name=user_cred.user.last_name,
            gender=user_cred.user.gender,
            email=user_cred.email,
        )


class RoleService(BaseService):
    model = DictRoles

    @classmethod
    @sqlalchemy_universal_decorator
    async def set_role(cls, session: AsyncSession, user: User, new_role: str) -> User:
        """Устанавливает новую роль для пользователя и сохраняет изменения в базе данных.

        Аргументы должны передаваться позиционно:
        - session: Асинхронная сессия SQLAlchemy.
        - user: Объект пользователя, чью роль нужно изменить.
        - new_role: Новая роль пользователя.
        """
        user.role_code = new_role
        await session.commit()
        return user

    @classmethod
    def to_response_body(cls, user: User, new_role: str):
        return UserRoleResponse(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            gender=user.gender,
            email=user.user_cred.email,
            role=new_role,
        )
