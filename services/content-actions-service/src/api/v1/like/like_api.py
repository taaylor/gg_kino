import logging
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Response, status
from models.models import Like

from api.v1.like.schemas import LikeRequest

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
    doc = await Like.find_one(Like.user_id == mock_user_id, Like.film_id == film_id)
    if doc:
        await doc.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    path="/{film_id}",
    status_code=status.HTTP_200_OK,
)
async def set_like(
    film_id: UUID,
    request_body: Annotated[
        LikeRequest,
        Body(description="Данные для добавления лайка в формате JSON"),
    ],
):
    # представим, что у нас в эндпоинте прошла проверка авторизации,
    # и пользователь с таким UUID
    mock_user_id = "d75589b0-0318-4360-b07a-88944c24bd92"
    mock_user_ids = [
        UUID("d75589b0-0318-4360-b07a-88944c24bd92"),
        UUID("cd4225d4-8087-4a42-aaf7-30a30e8a919d"),
        UUID("5580dfe4-9803-4291-8e6b-6e7df27d7032"),
        UUID("8c5d61fa-bcfc-4b91-9ced-5e16da90f4e7"),
    ]
    like_exist = await Like.find_one(
        Like.user_id == mock_user_id,
        Like.film_id == film_id,
    )
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


@router.get(
    path="/{film_id}",
)
async def get_like(
    film_id: UUID,
):
    # представим, что у нас в эндпоинте прошла проверка авторизации,
    # и пользователь с таким UUID
    # mock_user_id = UUID("d75589b0-0318-4360-b07a-88944c24bd92")

    # pipeline = [
    #     {"$match": {"film_id": film_id}},
    #     {"$group": {
    #         "_id": None,
    #         "avg_rating": {"$avg": "$rating"},
    #         "likes": {"$sum": {"$cond": [{"$eq": ["$rating", 10]}, 1, 0]}},
    #         "dislikes": {"$sum": {"$cond": [{"$eq": ["$rating", 0]}, 1, 0]}},
    #         "count": {"$sum": 1}
    #     }}
    # ]
    pipeline = [
        {"$match": {"film_id": film_id}},
        # {"$match": {"film_id": str(film_id)}},
        {"$group": {"_id": "$film_id", "avg_rating": {"$avg": "$rating"}}},
    ]
    cursor = Like.aggregate(pipeline)
    result = await cursor.to_list(length=1)
    # like = await Like.find_one(Like.user_id == mock_user_id, Like.film_id == film_id)

    return {
        "like": result,
    }
