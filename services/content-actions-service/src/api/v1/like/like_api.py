import logging
from typing import Annotated
from uuid import UUID

from api.v1.like.schemas import LikeRequest
from fastapi import APIRouter, Body, status
from models.models import Like

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
)
async def set_like(
    request_body: Annotated[
        LikeRequest, Body(description="Данные для добавления лайка в формате JSON")
    ],
):
    await Like(
        user_id=UUID("d75589b0-0318-4360-b07a-88944c24bd92"), film_id=request_body.film_id
    ).insert()
    return {
        "status": "ok",
    }


@router.get(
    path="/{film_id}",
)
async def get_like(
    film_id: UUID,
):
    like = await Like.find_one(Like.film_id == film_id)
    return {
        "status": "ok",
        "like": like,
    }
