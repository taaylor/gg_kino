import logging
from typing import Annotated
from uuid import UUID

from api.v1.review.schemas import (
    ReviewDetailResponse,
    ReviewModifiedRequest,
    ReviewModifiedResponse,
    ReviewRateResponse,
)
from auth_utils import LibAuthJWT, auth_dep
from core.config import app_config
from fastapi import APIRouter, Body, Depends, Path, Query, status
from models.enum_models import LikeEnum, SortedEnum
from rate_limite_utils import rate_limit
from services.review_service import ReviewService, get_review_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    path="/film/{film_id}",
    summary="Отдает рецензии по id фильма в зависимости от фильтрации",
    description="Отдает рецензии по id фильма в зависимости от фильтрации",
    response_model=list[ReviewDetailResponse],
)
@rate_limit()
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


@router.get(
    path="/user",
    summary="Отдает все рецензии оставленные пользователем",
    description="Отдает все рецензии оставленные пользователем",
    response_model=list[ReviewDetailResponse],
)
@rate_limit()
async def receive_reviews_user_films(  # noqa: WPS211
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
    user_id: Annotated[
        UUID | None,
        Query(
            description="Опциональный идентификатор пользователя, \
            позволяет получить рецензии конкретного пользователя. "
            "По умолчанию идентификатор берется из JWT"
        ),
    ] = None,
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
    await authorize.jwt_required()
    if not user_id:
        decrypted_token = await authorize.get_raw_jwt()
        user_id = UUID(decrypted_token.get("user_id"))
    return await review_service.get_user_reviews(user_id, page_number, page_size, sorted)


@router.post(
    path="/{film_id}",
    summary="Позволяет добавить пользователю рецензию к фильму",
    description="Добавить рецензию к фильму",
    response_model=ReviewModifiedResponse,
)
@rate_limit()
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


@router.put(
    path="/{review_id}",
    summary="Позволяет обновить текст рецензии",
    description="Позволяет обновить текст рецензии пользователя к фильму",
    response_model=ReviewModifiedResponse,
)
@rate_limit()
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
@rate_limit()
async def delete_review_film(
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    review_id: Annotated[UUID, Path(description="Идентификатор рецензии")],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
) -> None:
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    user_id = UUID(decrypted_token.get("user_id"))
    await review_service.delete_review(review_id, user_id)


@router.post(
    path="/rate/{review_id}",
    summary="Позволяет пользователю оценить рецензию",
    description="Позволяет пользователю оценить и изменить оценку рецензию (лайк/дизлайк)",
    response_model=ReviewRateResponse,
)
@rate_limit()
async def rate_review_film(
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    review_id: Annotated[UUID, Path(description="Идентификатор рецензии")],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
    mark: Annotated[LikeEnum, Query(description="лайк/дизлайк")],
) -> ReviewRateResponse:
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    user_id = UUID(decrypted_token.get("user_id"))
    return await review_service.rate_review(review_id, user_id, mark)


@router.delete(
    path="/rate/{review_id}",
    summary="Позволяет пользователю удалить оценку с рецензии",
    description="Позволяет пользователю удалить оценку с рецензии по id",
    status_code=status.HTTP_204_NO_CONTENT,
)
@rate_limit()
async def delete_rate_review_film(
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    review_id: Annotated[UUID, Path(description="Идентификатор рецензии")],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
):
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    user_id = UUID(decrypted_token.get("user_id"))
    return await review_service.delete_rate_review(user_id, review_id)
