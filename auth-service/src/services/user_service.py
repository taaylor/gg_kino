from models.models import DictRoles, User, UserCred
from passlib.hash import argon2
from services.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class UserService(BaseService):
    """
    Бизнес-логика для работы с моделью User.
    """

    model = User

    @classmethod
    async def set_username(cls, session: AsyncSession, user: User, new_username: str) -> User:
        """
        Устанавливает новое имя пользователя и сохраняет изменения в базе данных.

        Аргументы должны передаваться позиционно:
        - session: Асинхронная сессия SQLAlchemy.
        - user: Объект пользователя, чьё имя нужно изменить.
        - new_username: Новое имя пользователя.
        """
        user.username = new_username
        await session.commit()
        return user


class UserCredService(BaseService):
    model = UserCred

    @classmethod
    async def set_password(
        cls, session: AsyncSession, user_cred: UserCred, new_password: str
    ) -> UserCred:
        """
        Устанавливает новый пароль для пользователя и сохраняет изменения в базе данных.

        Аргументы должны передаваться позиционно:
        - session: Асинхронная сессия SQLAlchemy.
        - user_cred: Объект пользователя, чьё имя нужно изменить.
        - new_password: Новый пароль пользователя.
        """
        user_cred.password = argon2.hash(new_password)
        await session.commit()
        return user_cred


class RoleService(BaseService):
    model = DictRoles

    @classmethod
    async def set_role(cls, session: AsyncSession, user: User, new_role: str) -> User:
        """
        Устанавливает новую роль для пользователя и сохраняет изменения в базе данных.

        Аргументы должны передаваться позиционно:
        - session: Асинхронная сессия SQLAlchemy.
        - user: Объект пользователя, чью роль нужно изменить.
        - new_role: Новая роль пользователя.
        """
        user.role_code = new_role
        await session.commit()
        return user
