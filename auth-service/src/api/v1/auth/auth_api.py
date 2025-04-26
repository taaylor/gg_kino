from typing import Annotated

from api.v1.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
)
from fastapi import APIRouter, Body, Depends, Header
from services.auth_service import (
    LoginService,
    RegisterService,
    get_login_service,
    get_register_service,
)

router = APIRouter(prefix="/auth/v1")


@router.post(path="/register", response_model=None)
async def register(
    request_body: Annotated[RegisterRequest, Body()],
    register_service: Annotated[RegisterService, Depends(get_register_service)],
    user_agent: Annotated[str | None, Header()] = None,
) -> RegisterResponse:
    return await register_service.create_user(request_body, user_agent)


@router.post(path="/login", response_model=LoginResponse)
async def login(
    request_body: Annotated[LoginRequest, Body()],
    login_service: Annotated[LoginService, Depends(get_login_service)],
    user_agent: Annotated[str | None, Header()] = None,
) -> LoginResponse:
    return await login_service.login_user(request_body, user_agent)


@router.post(path="/refresh", response_model=RefreshResponse)
async def refresh(request_body: Annotated[RefreshRequest, Body()]) -> RefreshResponse:
    pass
