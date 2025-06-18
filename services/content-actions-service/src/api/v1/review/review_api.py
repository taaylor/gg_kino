import logging
from typing import Annotated
from uuid import UUID

from api.v1.review.schemas import (
    ReviewDetailResponse,
    ReviewModifiedRequest,
    ReviewModifiedResponse,
)
from auth_utils import LibAuthJWT, auth_dep
from core.config import app_config
from fastapi import APIRouter, Body, Depends, Path, Query, status
from models.enum_models import SortedEnum
from services.review_service import ReviewService, get_review_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    path="/{film_id}",
    summary="Отдает рецензии по id фильма в зависимости от фильтрации",
    description="Отдает рецензии по id фильма в зависимости от фильтрации",
    response_model=list[ReviewDetailResponse],
)
async def receive_reviews_film(
    film_id: Annotated[UUID, Path(description="Идентификатор фильма")],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
    page_number: Annotated[int, Query(ge=1, description="Номер страницы рецензий")] = 1,
    page_size: Annotated[
        int,
        Query(
            ge=app_config.min_page_size,
            le=app_config.max_page_size,
            description="Количестов рецензий на странице",
        ),
    ] = app_config.max_page_size,
    sorted: Annotated[
        SortedEnum, Query(description="Сортировка по параметру")
    ] = SortedEnum.CREATED_DESC,
) -> list[ReviewDetailResponse]:
    return await review_service.get_reviews(film_id, page_number, page_size, sorted)


@router.post(
    path="/{film_id}",
    summary="Позволяет добавить пользователю рецензию к фильму",
    description="Добавить рецензию к фильму",
    response_model=ReviewModifiedResponse,
)
async def append_review_film(
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    film_id: Annotated[UUID, Path(description="Идентификатор фильма")],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
    review_text: Annotated[ReviewModifiedRequest, Body(description="Текст рецензии")],
) -> ReviewModifiedResponse:
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    user_id = UUID(decrypted_token.get("user_id"))
    return await review_service.append_review(film_id, user_id, review_text)


@router.patch(
    path="/{review_id}",
    summary="Позволяет обновить текст рецензии",
    description="Позволяет обновить текст рецензии пользователя к фильму",
    response_model=ReviewModifiedResponse,
)
async def update_review_film(
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    review_id: Annotated[UUID, Path(description="Идентификатор рецензии")],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
    review_text: Annotated[ReviewModifiedRequest, Body(description="Измененный текст рецензии")],
) -> ReviewModifiedResponse:
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    user_id = UUID(decrypted_token.get("user_id"))
    return await review_service.update_review(review_id, user_id, review_text)


@router.delete(
    path="/{review_id}",
    summary="Позволяет удалить рецензию",
    description="Позволяет удалить рецензию пользователя к фильму",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review_film(
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    review_id: Annotated[UUID, Path(description="Идентификатор рецензии")],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
) -> None:
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    user_id = UUID(decrypted_token.get("user_id"))
    return await review_service.delete_review(review_id, user_id)
