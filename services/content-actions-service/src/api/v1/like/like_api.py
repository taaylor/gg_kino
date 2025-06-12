import logging
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from api.v1.like.schemas import LikeRequest
from fastapi import APIRouter, Body, Response, status
from models.models import Like

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
        LikeRequest, Body(description="Данные для добавления лайка в формате JSON")
    ],
):
    # представим, что у нас в эндпоинте прошла проверка авторизации,
    # и пользователь с таким UUID
    mock_user_id = UUID("d75589b0-0318-4360-b07a-88944c24bd92")
    like_exist = await Like.find_one(Like.user_id == mock_user_id, Like.film_id == film_id)
    if like_exist:
        like_exist.rating = request_body.rating
        like_exist.updated_at = datetime.now(timezone.utc)
        result = await like_exist.save()
    else:
        result = await Like(
            user_id=UUID("d75589b0-0318-4360-b07a-88944c24bd92"),
            film_id=film_id,
            rating=request_body.rating,
        ).insert()
    return {"status": "ok", "result": result}


@router.get(
    path="/{film_id}",
)
async def get_like(
    film_id: UUID,
):
    # представим, что у нас в эндпоинте прошла проверка авторизации,
    # и пользователь с таким UUID
    mock_user_id = UUID("d75589b0-0318-4360-b07a-88944c24bd92")
    like = await Like.find_one(Like.user_id == mock_user_id, Like.film_id == film_id)

    return {
        "like": like,
    }
