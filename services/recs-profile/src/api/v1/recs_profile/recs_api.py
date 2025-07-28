from typing import Annotated

from api.v1.recs_profile.schemas import UserRecsRequest, UserRecsResponse
from fastapi import APIRouter, Body

# from services.nlp_service import NlpService, get_nlp_service

router = APIRouter()


@router.post(
    "/fetch-user-recs",
    summary="Получить профиль рекомендаций",
    description="Получение рекомендательного профиля пользователя",
    response_model=UserRecsResponse,
)
async def fetch_films_by_user_query(
    # service: Annotated[NlpService, Depends(get_nlp_service)],
    request_body: Annotated[UserRecsRequest, Body],
) -> UserRecsResponse:

    return None
