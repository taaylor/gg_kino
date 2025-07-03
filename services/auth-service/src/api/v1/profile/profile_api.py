from typing import Annotated
from uuid import UUID

from api.v1.profile.schemas import ProfileResponse
from auth_utils import LibAuthJWT, auth_dep
from fastapi import APIRouter, Depends
from services.profile_service import ProfileService, get_profile_service

router = APIRouter()


@router.get(
    path="/",
    description="Возвращает профиль пользователя по id пользователя",
    summary="Получить профиль пользователя",
    response_model=ProfileResponse | None,
)
async def get_user_profile_info(
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
) -> ProfileResponse | None:
    await authorize.jwt_required()
    user_jwt_id = UUID((await authorize.get_raw_jwt()).get("user_id"))
    return await profile_service.get_user_data_profile(user_jwt_id)
