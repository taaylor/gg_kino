from typing import Annotated

from api.v1.recs_profile.schemas import UserRecsRequest, UserRecsResponse
from fastapi import APIRouter, Body, Depends
from services.recs_service import RecsService, get_recs_service

router = APIRouter()


@router.post(
    "/fetch-user-recs",
    summary="Получить профиль рекомендаций",
    description="Получение рекомендательного профиля пользователя",
    response_model=UserRecsResponse,
)
async def fetch_films_by_user_query(
    service: Annotated[RecsService, Depends(get_recs_service)],
    request_body: Annotated[UserRecsRequest, Body],
) -> UserRecsResponse:

    return await service.fetch_user_recs(request_body)
