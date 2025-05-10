import hashlib
import hmac
import logging
import secrets
import uuid
from functools import lru_cache
from typing import Any

from api.v1.auth.schemas import (
    EntryPoint,
    LoginRequest,
    LoginResponse,
    OAuthParams,
    OAuthSocialResponse,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
    SessionsHistory,
    YandexParams,
)
from core.config import app_config
from db.cache import Cache, get_cache
from db.postgres import get_session
from fastapi import Depends, HTTPException, status
from models.logic_models import SessionUserData
from models.models import User, UserCred
from services.auth_repository import AuthRepository, get_auth_repository
from services.base_service import BaseAuthService, MixinAuthRepository
from services.session_maker import SessionMaker, get_auth_session_maker
from sqlalchemy.ext.asyncio import AsyncSession
from utils.key_manager import pwd_context

logger = logging.getLogger(__name__)


DEFAULT_ROLE = app_config.default_role
CACHE_KEY_DROP_SESSION = app_config.jwt.cache_key_drop_session


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


class LogoutService(MixinAuthRepository):

    def __init__(self, repository: AuthRepository, session: AsyncSession, cache: Cache):
        super().__init__(repository, session)
        self.cache = cache

    async def logout_session(self, access_data: dict[str, Any]):
        user_data = SessionUserData.model_validate(access_data)
        current_session = user_data.session_id
        username = user_data.username

        await self.repository.drop_session_by_id(session=self.session, session_id=current_session)

        logger.info(f"Пользователь {username} вышел из сессии {current_session}")

        cache_key = CACHE_KEY_DROP_SESSION.format(
            user_id=user_data.user_id, session_id=current_session
        )

        await self.cache.background_set(
            key=cache_key,
            value=str(current_session),
            expire=app_config.jwt.refresh_token_lifetime_sec,
        )

    async def logout_all_sessions(self, access_data: dict[str, Any]):
        user_data = SessionUserData.model_validate(access_data)
        current_session = user_data.session_id
        username = user_data.username

        result = await self.repository.drop_sessions_except_current(
            session=self.session, current_session=current_session, user_id=user_data.user_id
        )

        for del_session in result:
            cache_key = CACHE_KEY_DROP_SESSION.format(
                user_id=user_data.user_id, session_id=del_session
            )
            await self.cache.background_set(
                key=cache_key,
                value=str(del_session),
                expire=app_config.jwt.refresh_token_lifetime_sec,
            )
            logger.info(f"Пользователь {username} вышел из сессии {del_session}")


class SessionService(MixinAuthRepository):

    async def get_history_session(
        self, access_data: dict[str, Any], page_size: int, page_number: int
    ) -> SessionsHistory:
        user_data = SessionUserData.model_validate(access_data)
        user_id = user_data.user_id
        current_session_id = user_data.session_id

        check_current_session = await self.repository.fetch_session_by_id(
            session=self.session, session_id=current_session_id
        )

        if not check_current_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Текущая сессия не найдена"
            )

        # получаем историю сессий
        history_sessions = await self.repository.fetch_history_sessions(
            session=self.session,
            current_session=check_current_session.session_id,
            user_id=user_id,
            page_size=page_size,
            page_number=page_number,
        )

        history_convert = [
            EntryPoint(user_agent=session.user_agent, created_at=session.created_at)
            for session in history_sessions
        ]

        return SessionsHistory(
            actual_user_agent=check_current_session.user_agent,
            create_at=check_current_session.created_at,
            history=history_convert,
        )


class OAuthSocialService(BaseAuthService):

    def _generate_signs_state() -> str:
        """Возвращает подписанный state"""
        nonce = secrets.token_urlsafe(16)

        secret = app_config.secret_key.encode("utf-8")
        signer = hmac.new(secret, digestmod=hashlib.sha256)
        signer.update(nonce.encode("utf-8"))
        signature = signer.hexdigest()

        return f"{nonce}-{signature}"

    def _validate_state(state: str) -> bool:
        """Валидирует state"""
        if not state.count("-") == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный формат state"
            )

        nonce, signature = state.split("-", 1)

        secret = app_config.secret_key.encode("utf-8")
        signer = hmac.new(secret, digestmod=hashlib.sha256)
        signer.update(nonce.encode("utf-8"))
        expected_signature = signer.hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Неверная подпись state"
            )

        return True

    def get_params_social(self) -> OAuthSocialResponse:
        state = secrets.token_urlsafe(16)

        yandex_separate_params = OAuthParams(
            client_id=app_config.yandex.client_id,
            scope=app_config.yandex.scope,
            response_type=app_config.yandex.response_type,
            authorize_url=app_config.yandex.authorize_url,
            state=state,
        )
        url = (
            "{url}?response_type={response_type}&client_id"
            "={client_id}&scope={scope}&state={state}".format(
                url=yandex_separate_params.authorize_url,
                response_type=yandex_separate_params.response_type,
                client_id=yandex_separate_params.client_id,
                scope=yandex_separate_params.scope,
                state=yandex_separate_params.state,
            )
        )

        yandex_params = YandexParams(params=yandex_separate_params, url_auth=url)

        return OAuthSocialResponse(yandex=yandex_params)


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


@lru_cache
def get_logout_service(
    session: AsyncSession = Depends(get_session),
    repository: AuthRepository = Depends(get_auth_repository),
    cache: Cache = Depends(get_cache),
) -> LogoutService:
    return LogoutService(repository=repository, session=session, cache=cache)


@lru_cache
def get_session_service(
    session: AsyncSession = Depends(get_session),
    repository: AuthRepository = Depends(get_auth_repository),
) -> SessionService:
    return SessionService(session=session, repository=repository)


@lru_cache
def get_oauth_social_service(
    session: AsyncSession = Depends(get_session),
    repository: AuthRepository = Depends(get_auth_repository),
    session_maker: SessionMaker = Depends(get_auth_session_maker),
) -> OAuthSocialService:
    return OAuthSocialService(repository=repository, session=session, session_maker=session_maker)
