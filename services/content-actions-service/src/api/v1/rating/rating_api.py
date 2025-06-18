import logging
from typing import Annotated
from uuid import UUID

from api.v1.rating.schemas import AvgRatingResponse, ScoreRequest, ScoreResponse
from auth_utils import LibAuthJWT, auth_dep
from fastapi import APIRouter, Body, Depends, Path, status
from services.rating_service import RatingService, get_rating_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.delete(
    path="/{film_id}",
    summary="Отзывает оценку поставленную авторизованным пользователем",
    description="Отзыв оценки фильма пользователем",
    response_description="Статус операции удаления с сообщением о результате",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_score(
    rating_service: Annotated[RatingService, Depends(get_rating_service)],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    film_id: Annotated[UUID, Path(description="Уникальный идентификатор фильма")],
):
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    user_id = UUID(decrypted_token.get("user_id"))
    await rating_service.delete_user_score(
        user_id=user_id,
        film_id=film_id,
    )


@router.post(
    path="/{film_id}",
    summary="Ставит/обновляет оценку поставленную авторизованным пользователем",
    description="Создание оценки фильма пользователем",
    response_description="Статус операции создания/обновления с сообщением о результате",
    status_code=status.HTTP_201_CREATED,
)
async def set_score(
    rating_service: Annotated[RatingService, Depends(get_rating_service)],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    film_id: Annotated[UUID, Path(description="Уникальный идентификатор фильма")],
    request_body: Annotated[
        ScoreRequest, Body(description="Данные для добавления лайка в формате JSON")
    ],
) -> ScoreResponse:
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    user_id = UUID(decrypted_token.get("user_id"))
    return await rating_service.set_user_score(
        user_id=user_id,
        film_id=film_id,
        score=request_body.score,
    )


@router.get(
    path="/{film_id}/rating",
    summary="Показывает рейтинг фильма (сумма оценок / кол-во оценок)",
    description="Рейтинг фильма",
    response_description="Статус операции показа рейтинга фильма с сообщением о результате",
    status_code=status.HTTP_200_OK,
)
async def get_avg_rating(
    rating_service: Annotated[RatingService, Depends(get_rating_service)],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    film_id: Annotated[UUID, Path(description="Уникальный идентификатор фильма")],
) -> AvgRatingResponse | None:
    user_id = None
    await authorize.jwt_optional()
    decrypted_token = await authorize.get_raw_jwt()
    if decrypted_token:
        user_id = UUID(decrypted_token.get("user_id"))
    result = await rating_service.get_average_rating(
        film_id=film_id,
        user_id=user_id,
    )
    return result


@router.post(
    path="/test-directory/{film_id}/{user_id}",
    status_code=status.HTTP_200_OK,
)
async def set_score_test(
    rating_service: Annotated[RatingService, Depends(get_rating_service)],
    film_id: UUID,
    user_id: UUID,
    request_body: Annotated[
        ScoreRequest, Body(description="Данные для добавления лайка в формате JSON")
    ],
) -> ScoreResponse:
    return await rating_service.set_user_score(
        user_id=user_id,
        film_id=film_id,
        score=request_body.score,
    )
