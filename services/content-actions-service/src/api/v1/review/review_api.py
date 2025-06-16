import logging
from typing import Annotated
from uuid import UUID

from api.v1.review.schemas import ReviewResponse, SortedReview
from fastapi import APIRouter, Depends, Path, Query
from services.review_service import ReviewService, get_review_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    path="/{film_id}",
    summary="Отдает рецензии по id фильма в зависимости от фильтрации",
    description="Отдает рецензии по id фильма в зависимости от фильтрации",
    response_model=list[ReviewResponse],
)
async def get_reviews_film(  # type: ignore
    film_id: Annotated[UUID, Path(description="Идентификатор фильма")],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
    page_number: Annotated[int, Query(description="Номер страницы")] = 1,
    page_total: Annotated[int, Query(description="Количестов рецензий на странице")] = 20,
    sorted: Annotated[
        SortedReview, Query(description="Сортировка по параметру")
    ] = SortedReview.CREATED_ASC,
) -> list[ReviewResponse]:
    pass  # type: ignore
