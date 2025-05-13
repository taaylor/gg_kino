import logging
from typing import Annotated

from api.v1.auth.schemas import (
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
    SessionsHistory,
)
from auth_utils import LibAuthJWT, auth_dep
from fastapi import APIRouter, Body, Depends, Query, Request
from services.auth_service import (
    LoginService,
    LogoutService,
    RefreshService,
    RegisterService,
    SessionService,
    get_login_service,
    get_logout_service,
    get_refresh_service,
    get_register_service,
    get_session_service,
)
from rate_limite_utils import rate_limit, rate_limit_leaky_bucket


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    path="/register",
    response_model=RegisterResponse,
    summary="Регистрация нового пользователя",
    description="Создает нового пользователя в системе на основе предоставленных данных.",
)
@rate_limit_leaky_bucket()
async def register(
    request: Request,
    request_body: Annotated[RegisterRequest, Body()],
    register_service: Annotated[RegisterService, Depends(get_register_service)],
) -> RegisterResponse:
    user_agent = request.headers.get("user-agent")
    return await register_service.create_user(request_body, user_agent)


@router.post(
    path="/login",
    response_model=LoginResponse,
    summary="Авторизация пользователя",
    description="Авторизует пользователя в системе и возвращает access и refresh токены.",
)
@rate_limit_leaky_bucket()
async def login(
    request: Request,
    request_body: Annotated[LoginRequest, Body()],
    login_service: Annotated[LoginService, Depends(get_login_service)],
) -> LoginResponse:
    user_agent = request.headers.get("user-agent")
    return await login_service.login_user(request_body, user_agent)


@router.post(
    path="/refresh",
    response_model=RefreshResponse,
    summary="Обновить сессию с помощью refresh токена",
    description="Обновляет сессию пользователя, используя предоставленный refresh токен.",
)
@rate_limit_leaky_bucket()
async def refresh(
    request: Request,
    refresh_service: Annotated[RefreshService, Depends(get_refresh_service)],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> RefreshResponse:
    await authorize.jwt_refresh_token_required()
    session_id = await authorize.get_jwt_subject()
    user_agent = request.headers.get("user-agent")
    logger.info(f"Из рефреш токена получена: {session_id=}")
    return await refresh_service.refresh_session(session_id, user_agent)


@router.post(
    path="/logout",
    summary="Выйти из текущего аккаунта",
    description="Закрывает текущую сессию пользователя",
    response_model=MessageResponse,
)
@rate_limit()
async def logout(
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    logout_service: Annotated[LogoutService, Depends(get_logout_service)],
) -> MessageResponse:
    await authorize.jwt_required()
    access_data = await authorize.get_raw_jwt()
    await logout_service.logout_session(access_data)
    return MessageResponse(message="Вы успешно вышли из аккаунта!")


@router.post(
    path="/logout-all",
    summary="Выйти из всех аккаунтов, кроме текущего",
    description="Закрывает все активные сессии пользователя, кроме текущей",
    response_model=MessageResponse,
)
@rate_limit()
async def logout_all(
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    logout_service: Annotated[LogoutService, Depends(get_logout_service)],
) -> MessageResponse:
    await authorize.jwt_required()
    access_data = await authorize.get_raw_jwt()
    await logout_service.logout_all_sessions(access_data)
    return MessageResponse(message="Вы успешно вышли из всех аккаунтов!")


@router.get(
    path="/entry-history",
    summary="Последние действия в аккаунте",
    description="Отдает информацию о последних действиях в аккаунте пользователя",
)
@rate_limit_leaky_bucket()
async def entry_history(
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    sessions_service: Annotated[SessionService, Depends(get_session_service)],
    page_size: Annotated[
        int, Query(ge=1, le=50, description="Количество записей на странице")
    ] = 25,
    page_number: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
) -> SessionsHistory:
    await authorize.jwt_required()
    access_data = await authorize.get_raw_jwt()
    history = await sessions_service.get_history_session(access_data, page_size, page_number)
    return history
