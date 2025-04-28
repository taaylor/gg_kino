import logging
import uuid
from functools import lru_cache

from api.v1.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
)
from core.config import app_config
from db.postgres import get_session
from fastapi import Depends, HTTPException, status
from models.logic_models import SessionUserData
from models.models import User, UserCred
from passlib.context import CryptContext
from services.auth_repository import AuthRepository, get_auth_repository
from services.base_service import BaseAuthService
from services.session_maker import SessionMaker, get_auth_session_maker
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

DEFAULT_ROLE = app_config.default_role


class RegisterService(BaseAuthService):

    async def create_user(self, user_data: RegisterRequest, user_agent: str) -> RegisterResponse:
        logger.debug(
            f"Обработка запроса на создание пользователя {user_data.username=}, {user_agent=}"
        )
        # Проверка уникальности username
        if await self.repository.fetch_user_by_name(
            session=self.session, username=user_data.username
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Полльзователь с таким именем уже существует",
            )
        logger.info(f"Пользователь предоставил имя, которого ещё нет в БД {user_data.username}")

        # Проверка уникальности email
        if await self.repository.fetch_user_by_email(session=self.session, email=user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Полльзователь с таким адресом почты уже существует",
            )
        logger.info(
            f"Пользователь предоставил электронную почту, которой ещё нет в БД: {user_data.email}"
        )

        # Подготовка данных для записи в БД
        user = User(
            id=uuid.uuid4(),
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            gender=user_data.gender,
            role_code=DEFAULT_ROLE,
        )

        hashed_password = pwd_context.hash(user_data.password)
        user_cred = UserCred(user_id=user.id, email=user_data.email, password=hashed_password)
        user_permissions = await self.repository.fetch_permissions_for_role(
            session=self.session, role_code=user.role_code
        )
        logger.debug(
            f"Для пользователя {user.username=} с ролью: {user.role_code}, получены разрешения: {user_permissions=}"  # noqa: E501
        )

        session_user_data = SessionUserData(
            user_id=user.id,
            username=user.username,
            user_agent=user_agent,
            role_code=user.role_code,
            permissions=user_permissions,
        )

        # Создание экземпляра сессии и токенов
        user_tokens, user_session, user_session_hist = await self.session_maker.create_session(
            user_data=session_user_data
        )

        # Запись всех данных для нового пользователя в БД
        await self.repository.create_user_in_repository(
            session=self.session,
            user=user,
            user_cred=user_cred,
            user_session=user_session,
            user_session_hist=user_session_hist,
        )

        logger.info(f"Создан пользователь: {user.id=}, {user.username=}")
        logger.info(
            f"Для пользоватлея {user.username} создана новая сессия: {user_session.session_id=}"
        )
        return RegisterResponse(
            user_id=user.id,
            username=user.username,
            email=user_cred.email,
            first_name=user.first_name,
            last_name=user.last_name,
            gender=user.gender,
            session=user_tokens,
        )


class LoginService(BaseAuthService):

    async def login_user(self, user_data: LoginRequest, user_agent: str) -> LoginResponse:
        logger.info(f"Запрошена аутентификация для пользователя с email: {user_data.email}")

        # Находим пользователя в БД
        user_cred = await self.repository.fetch_usercred_by_email(
            session=self.session, email=user_data.email
        )

        if not user_cred:
            logger.info(f"В БД не найден пользователь с email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неверный пароль или пользователь с email: {user_data.email} не существует",
            )

        if not pwd_context.verify(user_data.password, user_cred.password):
            logger.warning(f"При попытке авторизации {user_data.email} был введён неверный пароль")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неверный пароль или пользователь с email: {user_data.email} не существует",
            )

        user = await self.repository.fetch_user_by_email(
            session=self.session, email=user_data.email
        )
        user_permissions = await self.repository.fetch_permissions_for_role(
            session=self.session, role_code=user.role_code
        )

        session_user_data = SessionUserData(
            user_id=user.id,
            username=user.username,
            user_agent=user_agent,
            role_code=user.role_code,
            permissions=user_permissions,
        )

        # Создание экземпляра сессии и токенов
        user_tokens, user_session, user_session_hist = await self.session_maker.create_session(
            user_data=session_user_data
        )

        await self.repository.create_session_in_repository(
            session=self.session,
            user_session=user_session,
            user_session_hist=user_session_hist,
        )

        logger.info(
            f"Для пользоватлея {user.username} создана новая сессия: {user_session.session_id=}"
        )

        return LoginResponse(
            access_token=user_tokens.access_token,
            refresh_token=user_tokens.refresh_token,
            expires_at=user_session.expires_at,
        )


class RefreshService(BaseAuthService):
    async def refresh_session(self, session_id: uuid.UUID, user_agent: str) -> RefreshResponse:
        logger.info(f"Запрошен рефреш сессии для {session_id=}")

        current_session = await self.repository.fetch_session_by_id(
            session=self.session, session_id=session_id
        )

        if not current_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невозможно обновить токены, сессия не найдена",
            )

        user = await self.repository.fetch_user_by_id(
            session=self.session, user_id=current_session.user_id
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не найден пользователь для полученной сессии",
            )

        user_permissions = await self.repository.fetch_permissions_for_role(
            session=self.session, role_code=user.role_code
        )
        session_user_data = SessionUserData(
            user_id=user.id,
            session_id=current_session.session_id,
            username=user.username,
            user_agent=user_agent,
            role_code=user.role_code,
            permissions=user_permissions,
        )
        user_tokens, updated_session = await self.session_maker.update_session(
            user_data=session_user_data
        )

        await self.repository.update_session_in_repository(
            session=self.session, user_session=updated_session
        )

        logger.info(
            f"Обновлена сессия: {session_user_data.session_id=} для пользователя: {session_user_data.user_id}"  # noqa: E501
        )

        return RefreshResponse(
            access_token=user_tokens.access_token,
            refresh_token=user_tokens.refresh_token,
            expires_at=user_tokens.expires_at,
        )


@lru_cache
def get_register_service(
    session: AsyncSession = Depends(get_session),
    repository: AuthRepository = Depends(get_auth_repository),
    session_maker: SessionMaker = Depends(get_auth_session_maker),
) -> RegisterService:
    return RegisterService(repository=repository, session=session, session_maker=session_maker)


@lru_cache
def get_login_service(
    session: AsyncSession = Depends(get_session),
    repository: AuthRepository = Depends(get_auth_repository),
    session_maker: SessionMaker = Depends(get_auth_session_maker),
) -> LoginService:
    return LoginService(repository=repository, session=session, session_maker=session_maker)


@lru_cache
def get_refresh_service(
    session: AsyncSession = Depends(get_session),
    repository: AuthRepository = Depends(get_auth_repository),
    session_maker: SessionMaker = Depends(get_auth_session_maker),
) -> RefreshService:
    return RefreshService(repository=repository, session=session, session_maker=session_maker)
