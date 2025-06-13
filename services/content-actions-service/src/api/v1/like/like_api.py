import logging
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from api.v1.like.schemas import LikeRequest, OutputRating
from fastapi import APIRouter, Body, status  # ,Depends
from models.models import Like
from services.like_repository import RatingRepository
from services.like_service import RatingService  # , get_rating_service

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
    # doc = await Like.find_one(Like.user_id == mock_user_id, Like.film_id == film_id)
    # if doc:
    #     await doc.delete()
    # await RatingRepository.delete_document(Like.user_id == mock_user_id, Like.film_id == film_id)
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
        LikeRequest, Body(description="Данные для добавления лайка в формате JSON")
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
    like_exist = await Like.find_one(Like.user_id == mock_user_id, Like.film_id == film_id)
    if like_exist:
        like_exist.rating = request_body.rating
        like_exist.updated_at = datetime.now(timezone.utc)
        result = await like_exist.save()
    else:
        # result = await Like(
        #     user_id=UUID("d75589b0-0318-4360-b07a-88944c24bd92"),
        #     film_id=film_id,
        #     rating=request_body.rating,
        # ).insert()
        # ! -=-=-=-=-=-=-=- временный вариант -=-=-=-=-=-=-=-
        for user_id in mock_user_ids:
            result = await Like(
                user_id=user_id,
                film_id=film_id,
                rating=request_body.rating,
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
        LikeRequest, Body(description="Данные для добавления лайка в формате JSON")
    ],
):
    # result = await RatingRepository.upsert(
    #     Like.user_id == user_id,
    #     Like.film_id == film_id,
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
        rating=request_body.rating,
    )
    return result


@router.get(
    path="/{film_id}/tempr",
)
async def get_like(
    film_id: UUID,
):
    # like = await Like.find_one(Like.user_id == mock_user_id, Like.film_id == film_id)
    # a = 1
    doc = (
        await Like.find(Like.film_id == film_id)
        .aggregate(
            [
                {
                    "$group": {
                        "_id": "$film_id",
                        "avg_rating": {"$avg": "$rating"},
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
        "like": doc,
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
