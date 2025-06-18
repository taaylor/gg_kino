import json
import logging
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from api.v1.review.schemas import (
    ReviewDetailResponse,
    ReviewModifiedRequest,
    ReviewModifiedResponse,
)
from core.config import app_config
from db.cache import Cache, get_cache
from fastapi import Depends, HTTPException, status
from models.enum_models import SortedEnum
from models.models import Review
from services.review_repository import (
    ReviewLikeRepository,
    ReviewRepository,
    get_review_like_repository,
    get_review_repository,
)

logger = logging.getLogger(__name__)


class ReviewService:
    CACHE_KEYS = {
        "list_review": "review:{film_id}:{sorted}:{page_number}:{page_size}",
    }

    __slots__ = (
        "cache",
        "review_repository",
        "review_like_repository",
    )

    def __init__(
        self,
        cache: Cache,
        review_repository: ReviewRepository,
        review_like_repository: ReviewLikeRepository,
    ):
        self.cache = cache
        self.review_repository = review_repository
        self.review_like_repository = review_like_repository

    async def get_reviews(
        self, film_id: UUID, page_number: int, page_size: int, sorted: SortedEnum
    ) -> list[ReviewDetailResponse]:
        """
        Получает список рецензий для фильма с пагинацией и сортировкой.

        Args:
            film_id (UUID): Идентификатор фильма, для которого запрашиваются рецензии.
            page_number (int): Номер страницы для пагинации (нумерация начинается с 1).
            page_size (int): Количество рецензий на одной странице (от 1 до 25).
            sorted (SortedEnum): Поле и порядок сортировки (например, по дате создания).

        Returns:
            list[ReviewDetailResponse]: Список рецензий в формате `ReviewDetailResponse`.
            Если рецензии не найдены, возвращается пустой список.
        """

        cache_key = self.CACHE_KEYS["list_review"].format(
            film_id=film_id, sorted=sorted.value, page_number=page_number, page_size=page_size
        )

        logger.debug(f"Заправшиваю кеш по ключу {cache_key}...")
        reviews_cache = await self.cache.get(cache_key)
        if reviews_cache:
            return [ReviewDetailResponse.model_validate(obj) for obj in json.loads(reviews_cache)]

        logger.debug(
            f"В кеше данных не оказалось делаю запрос по \
            рецензиям с параметрами: {film_id=}, {page_number=}, {page_size}, {sorted.value=}"
        )

        reviews = await self.review_repository.get_reviews(film_id, page_number, page_size, sorted)
        logger.debug(f"Получено {len(reviews)} рецензий")

        if reviews:
            convert_data = [ReviewDetailResponse(**obj.model_dump()) for obj in reviews]
            await self.cache.background_set(
                key=cache_key,
                value=json.dumps([obj.model_dump(mode="json") for obj in convert_data]),
                expire=app_config.cache_expire_in_seconds,
            )
            return convert_data
        return []

    async def append_review(
        self, film_id: UUID, user_id: UUID, review_text: ReviewModifiedRequest
    ) -> ReviewModifiedResponse:
        """
        Добавляет новую рецензию к фильму от имени пользователя.

        Args:
            film_id (UUID): Идентификатор фильма, к которому добавляется рецензия.
            user_id (UUID): Идентификатор пользователя, добавляющего рецензию.
            review_text (ReviewModifiedRequest): Объект с текстом рецензии.

        Returns:
            ReviewModifiedResponse: Объект созданной рецензии со всеми полями.
        """
        review = await self.review_repository.insert_document(
            user_id=user_id, film_id=film_id, text=review_text.text
        )
        logger.debug(f"Пользователь {user_id=} добавляет рецензию {review.id=} к фильму {film_id=}")
        return ReviewModifiedResponse(**review.model_dump())

    async def update_review(
        self, review_id: UUID, user_id: UUID, review_text: ReviewModifiedRequest
    ) -> ReviewModifiedResponse:
        """
        Обновляет текст рецензии, созданной указанным пользователем.

        Args:
            review_id (UUID): Идентификатор рецензии, которую нужно обновить.
            user_id (UUID): Идентификатор пользователя, обновляющего рецензию.
            review_text (ReviewModifiedRequest): Объект, содержащий новый текст рецензии.

        Returns:
            ReviewModifiedResponse: Объект с обновленными данными рецензии.

        """

        review = await self.review_repository.get_document(
            Review.id == review_id, Review.user_id == user_id
        )

        if not review:
            logger.debug(f"Рецензия {review_id=} от пользователя {user_id=} не найдена")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Документ не найден"
            )

        update_review = await self.review_repository.update_document(review, text=review_text.text)
        logger.debug(f"Пользователь {user_id=} обновил рецензию {review_id=}")

        return ReviewModifiedResponse(**update_review.model_dump())

    async def delete_review(self, review_id: UUID, user_id: UUID) -> None:
        """
        Удаляет рецензию, созданную указанным пользователем.

        Args:
            review_id (UUID): Идентификатор рецензии, которую нужно удалить.
            user_id (UUID): Идентификатор пользователя, удаляющего рецензию.

        Returns:
            None: При успешном удалении рецензии.
        """

        review = await self.review_repository.delete_document(
            Review.id == review_id, Review.user_id == user_id
        )

        if review:
            logger.debug(f"Пользователь {user_id=} удалил рецензию {review_id=}")
            return None

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Рецензия {review_id=} не найдена"
        )


@lru_cache()
def get_review_service(
    cache: Annotated[Cache, Depends(get_cache)],
    review_repository: Annotated[ReviewRepository, Depends(get_review_repository)],
    review_like_repository: Annotated[ReviewLikeRepository, Depends(get_review_like_repository)],
) -> ReviewService:
    return ReviewService(cache, review_repository, review_like_repository)
