from typing import Annotated

from api.v1.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
)
from fastapi import APIRouter, Body, Depends
from services.auth_service import RegisterService, get_register_service

router = APIRouter(prefix="/auth/v1")


@router.post(path="/register", response_model=None)
async def register(
    request_body: Annotated[RegisterRequest, Body()],
    register_service: Annotated[RegisterService, Depends(get_register_service)],
) -> RegisterResponse:
    return await register_service.create_user(request_body)


@router.post(path="/login", response_model=LoginResponse)
async def login(request_body: Annotated[LoginRequest, Body()]) -> LoginResponse:
    pass


@router.post(path="/refresh", response_model=RefreshResponse)
async def refresh(request_body: Annotated[RefreshRequest, Body()]) -> RefreshResponse:
    pass
