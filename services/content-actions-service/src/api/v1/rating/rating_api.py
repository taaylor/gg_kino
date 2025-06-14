import logging
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from api.v1.rating.schemas import OutputRating, ScoreRequest
from fastapi import APIRouter, Body, status  # ,Depends
from models.models import Rating
from services.rating_repository import RatingRepository
from services.rating_service import RatingService  # , get_rating_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.delete(
    path="/{film_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_like(
    film_id: UUID,
):
    # представим, что у нас в эндпоинте прошла проверка авторизации,
    # и пользователь с таким UUID
    mock_user_id = UUID("d75589b0-0318-4360-b07a-88944c24bd92")
    # a = 1
    # doc = await Rating.find_one(Rating.user_id == mock_user_id, Rating.film_id == film_id)
    # if doc:
    #     await doc.delete()
    # await RatingRepository.delete_document(
    #     Rating.user_id == mock_user_id,
    #     Rating.film_id == film_id
    #     )
    # return Response(status_code=status.HTTP_204_NO_CONTENT)
    rating_service = RatingService(RatingRepository)
    await rating_service.delete_user_score(
        mock_user_id,
        film_id,
    )
    return None


@router.put(
    path="/{film_id}",
    status_code=status.HTTP_200_OK,
)
async def set_tempr_like(
    film_id: UUID,
    request_body: Annotated[
        ScoreRequest, Body(description="Данные для добавления лайка в формате JSON")
    ],
):
    # представим, что у нас в эндпоинте прошла проверка авторизации,
    # и пользователь с таким UUID
    mock_user_id = UUID("d75589b0-0318-4360-b07a-88944c24bd92")
    mock_user_ids = [
        UUID("d75589b0-0318-4360-b07a-88944c24bd92"),
        UUID("cd4225d4-8087-4a42-aaf7-30a30e8a919d"),
        UUID("5580dfe4-9803-4291-8e6b-6e7df27d7032"),
        UUID("8c5d61fa-bcfc-4b91-9ced-5e16da90f4e7"),
    ]
    score_exist = await Rating.find_one(Rating.user_id == mock_user_id, Rating.film_id == film_id)
    if score_exist:
        score_exist.score = request_body.score
        score_exist.updated_at = datetime.now(timezone.utc)
        result = await score_exist.save()
    else:
        # result = await Rating(
        #     user_id=UUID("d75589b0-0318-4360-b07a-88944c24bd92"),
        #     film_id=film_id,
        #     rating=request_body.rating,
        # ).insert()
        # ! -=-=-=-=-=-=-=- временный вариант -=-=-=-=-=-=-=-
        for user_id in mock_user_ids:
            result = await Rating(
                user_id=user_id,
                film_id=film_id,
                score=request_body.score,
            ).insert()
        # ! -=-=-=-=-=-=-=- временный вариант -=-=-=-=-=-=-=-
    return {"status": "ok", "result": result}


@router.post(
    path="/{film_id}/next-mock-user-id/{user_id}",
    status_code=status.HTTP_200_OK,
)
async def set_score(
    film_id: UUID,
    user_id: UUID,
    request_body: Annotated[
        ScoreRequest, Body(description="Данные для добавления лайка в формате JSON")
    ],
):
    # result = await RatingRepository.upsert(
    #     Rating.user_id == user_id,
    #     Rating.film_id == film_id,
    #     update_fields=["rating", "lalala"],
    #     # update_fields=[],
    #     user_id=user_id,
    #     film_id=film_id,
    #     rating=request_body.rating,
    # )
    rating_service = RatingService(RatingRepository)
    result = await rating_service.set_user_score(
        user_id=user_id,
        film_id=film_id,
        score=request_body.score,
    )
    return result


@router.get(
    path="/{film_id}/tempr",
)
async def get_like(
    film_id: UUID,
):
    # like = await Rating.find_one(Rating.user_id == mock_user_id, Rating.film_id == film_id)
    # a = 1
    doc = (
        await Rating.find(Rating.film_id == film_id)
        .aggregate(
            [
                {
                    "$group": {
                        "_id": "$film_id",
                        "avg_rating": {"$avg": "$score"},
                        "count_votes": {"$sum": 1},
                    }
                }
            ],
            projection_model=OutputRating,
        )
        .to_list()
    )
    if not doc:
        return None
    # doc = [
    # OutputRating(id=UUID('cd4225d4-8087-4a42-aaf7-30a30e8a919d'),
    # rating=3.0, count_votes=4)]
    # doc = doc[0]
    # doc.model_dump()
    return {
        "score": doc,
    }


# cd4225d4-8087-4a42-aaf7-30a30e8a919d


@router.get(
    path="/{film_id}",
)
async def get_avg_rating(
    film_id: UUID,
    # rating_service: Annotated[RatingService, Depends(get_rating_service)],
):
    rating_service = RatingService(RatingRepository)
    result = await rating_service.get_average_rating(film_id)
    return result
