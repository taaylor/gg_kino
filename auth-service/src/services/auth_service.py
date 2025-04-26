import datetime
import logging
import uuid
from functools import lru_cache

from api.v1.auth.schemas import RegisterRequest, RegisterResponse, Session
from core.config import app_config
from db.cache import Cache, get_cache
from db.postgres import get_session
from fastapi import Depends, HTTPException, status
from models.logic_models import SessionUserDataData
from models.models import User, UserCred, UserSession, UserSessionsHist
from passlib.context import CryptContext
from services.auth_repository import AuthReository, get_auth_repository
from sqlalchemy.ext.asyncio import AsyncSession
from utils.key_manager import JWTProcessor, get_key_manager

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["argon2"])

DEFAULT_ROLE = app_config.default_role


class SessionMaker:
    def __init__(self, key_manager: JWTProcessor):
        self.key_manager = key_manager

    async def create_session(self, user_data: SessionUserDataData) -> Session:
        user_data.session_id = uuid.uuid4()

        access_token, refresh_token = await self._create_tokens(user_data=user_data)

        user_session = UserSession(
            session_id=user_data.session_id,
            user_id=user_data.user_id,
            user_agent=user_data.user_agent,
            refresh_token=refresh_token,
            expires_at=datetime.datetime.now()
            + datetime.timedelta(seconds=app_config.jwt.refresh_token_lifetime_sec),
        )

        user_session_hist = UserSessionsHist(
            session_id=user_session.session_id,
            user_id=user_session.user_id,
            user_agent=user_session.user_agent,
            expires_at=user_session.expires_at,
        )

        user_tokens = Session(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=user_session.expires_at,
        )

        return user_tokens, user_session, user_session_hist

    async def _create_tokens(self, user_data: SessionUserDataData):
        access_token, refresh_token = await self.key_manager.create_tokens(user_data=user_data)
        return access_token, refresh_token


class RegisterService:
    def __init__(
        self, repository: AuthReository, session: AsyncSession, session_maker: SessionMaker
    ):
        self.repository = repository
        self.session = session
        self.session_maker = session_maker

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

        session_user_data = SessionUserDataData(
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

        return RegisterResponse(
            user_id=user.id,
            username=user.username,
            email=user_cred.email,
            first_name=user.first_name,
            last_name=user.last_name,
            gender=user.gender,
            session=user_tokens,
        )


class LoginService:
    def __init__(self, repository: AsyncSession):
        self.repository = repository

    pass


class RefreshService:
    def __init__(self, repository: AsyncSession):
        self.repository = repository

    pass


@lru_cache
def get_register_service(
    session: AsyncSession = Depends(get_session),
    key_manager: JWTProcessor = Depends(get_key_manager),
    repository: AuthReository = Depends(get_auth_repository),
) -> RegisterService:
    repository = repository
    session_maker = SessionMaker(key_manager=key_manager)
    return RegisterService(repository=repository, session=session, session_maker=session_maker)


@lru_cache
def get_login_service(repository: AsyncSession = Depends(get_session)) -> RegisterService:
    pass


@lru_cache
def get_refresh_service(
    cache: Cache = Depends(get_cache), session: AsyncSession = Depends(get_session)
) -> RegisterService:
    pass
