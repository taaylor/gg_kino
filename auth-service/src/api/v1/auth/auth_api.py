from typing import Annotated

from api.v1.auth.schemas import (  # RegisterResponce,
    LoginRequest,
    LoginResponce,
    RefreshRequest,
    RefreshResponce,
    RegisterRequest,
)
from fastapi import APIRouter, Body, Depends
from services.auth_service import RegisterService, get_register_service

router = APIRouter(prefix="/auth/v1")


# @router.post(path="/register", response_model=RegisterResponce)
# async def register(
#     request_body: Annotated[RegisterRequest, Body()],
#  register_service=Depends(get_register_service)
# ) -> RegisterResponce:


@router.post(path="/register", response_model=None)
async def register(
    request_body: Annotated[RegisterRequest, Body()],
    register_service: Annotated[RegisterService, Depends(get_register_service)],
) -> None:

    await register_service.create_user(request_body)


@router.post(path="/login", response_model=LoginResponce)
async def login(request_body: Annotated[LoginRequest, Body()]) -> LoginResponce:
    pass


@router.post(path="/refresh", response_model=RefreshResponce)
async def refresh(request_body: Annotated[RefreshRequest, Body()]) -> RefreshResponce:
    pass
