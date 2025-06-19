import json
import logging
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from api.v1.review.schemas import (
    ReviewDetailResponse,
    ReviewModifiedRequest,
    ReviewModifiedResponse,
    ReviewRateResponse,
)
from core.config import app_config
from db.cache import Cache, get_cache
from fastapi import Depends, HTTPException, status
from models.enum_models import LikeEnum, SortedEnum
from models.models import Review, ReviewLike
from services.review_repository import (
    ReviewLikeRepository,
    ReviewRepository,
    get_review_like_repository,
    get_review_repository,
)
from utils.film_id_validator import FilmIdValidator, get_film_id_validator

logger = logging.getLogger(__name__)


class ReviewService:  # noqa: WPS214
    CACHE_KEYS = {
        "list_review": "review:film:{film_id}:{sorted}:{page_number}:{page_size}",
        "user_review": "review:user:{user_id}:{sorted}:{page_number}:{page_size}",
    }

    __slots__ = ("cache", "review_repository", "review_like_repository", "film_validator")

    def __init__(
        self,
        cache: Cache,
        review_repository: ReviewRepository,
        review_like_repository: ReviewLikeRepository,
        film_validator: FilmIdValidator,
    ):
        self.cache = cache
        self.review_repository = review_repository
        self.review_like_repository = review_like_repository
        self.film_validator = film_validator

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

        cache_key = self.__class__.CACHE_KEYS["list_review"].format(
            film_id=film_id, sorted=sorted.value, page_number=page_number, page_size=page_size
        )

        logger.debug(f"Заправшиваю кеш по ключу {cache_key}...")
        reviews_cache = await self.cache.get(cache_key)
        if reviews_cache:
            return [ReviewDetailResponse.model_validate(obj) for obj in json.loads(reviews_cache)]

        logger.info(
            f"В кеше данных не оказалось делаю запрос по \
            рецензиям с параметрами: {film_id=}, {page_number=}, {page_size}, {sorted.value=}"
        )

        await self.film_validator.validate_film_id(film_id)

        reviews = await self.review_repository.get_reviews(film_id, page_number, page_size, sorted)
        logger.info(f"Получено {len(reviews)} рецензий к фильму {film_id=}")

        if reviews:
            convert_review = [ReviewDetailResponse(**obj.model_dump()) for obj in reviews]
            await self.cache.background_set(
                key=cache_key,
                value=json.dumps([obj.model_dump(mode="json") for obj in convert_review]),
                expire=app_config.cache_expire_in_seconds,
            )
            return convert_review
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
        await self.film_validator.validate_film_id(film_id)

        review = await self.review_repository.insert_document(
            user_id=user_id, film_id=film_id, text=review_text.text
        )
        logger.info(f"Пользователь {user_id=} добавляет рецензию {review.id=} к фильму {film_id=}")
        await self.cache.background_destroy_all_by_pattern(f"review:user:{user_id}:*")
        await self.cache.background_destroy_all_by_pattern(f"review:film:{film_id}:*")
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
            logger.info(f"Рецензия {review_id=} от пользователя {user_id=} не найдена")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Документ не найден"
            )

        update_review = await self.review_repository.update_document(review, text=review_text.text)
        logger.info(f"Пользователь {user_id=} обновил рецензию {review_id=}")
        await self.cache.background_destroy_all_by_pattern(f"review:user:{user_id}:*")
        await self.cache.background_destroy_all_by_pattern(f"review:film:{update_review.film_id}:*")

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

        if not review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Рецензия {review_id=} не найдена"
            )
        await self.cache.background_destroy_all_by_pattern(f"review:user:{user_id}:*")
        logger.info(f"Пользователь {user_id=} удалил рецензию {review_id=}")

    async def get_user_reviews(
        self, user_id: UUID, page_number: int, page_size: int, sorted: SortedEnum
    ) -> list[ReviewDetailResponse]:
        """
        Получает список рецензий пользователя с пагинацией и сортировкой, используя кэширование.

        Args:
            user_id (UUID): Идентификатор пользователя, чьи рецензии запрашиваются.
            page_number (int): Номер страницы для пагинации (начинается с 1).
            page_size (int): Количество рецензий на одной странице.
            sorted (SortedEnum): Порядок сортировки рецензий (например, по дате или рейтингу).

        Returns:
            list[ReviewDetailResponse]: Список рецензий пользователя, преобразованных в объекты
            `ReviewDetailResponse`. Если рецензии отсутствуют, возвращается пустой список.
        """

        cache_key = self.__class__.CACHE_KEYS["user_review"].format(
            user_id=user_id, sorted=sorted.value, page_number=page_number, page_size=page_size
        )

        logger.debug(f"Заправшиваю кеш по ключу {cache_key}...")
        reviews_cache = await self.cache.get(cache_key)
        if reviews_cache:
            return [ReviewDetailResponse.model_validate(obj) for obj in json.loads(reviews_cache)]

        logger.info(
            f"В кеше данных не оказалось делаю запрос по \
            рецензиям с параметрами: {user_id=}, {page_number=}, {page_size}, {sorted.value=}"
        )

        reviews = await self.review_repository.get_user_reviews(
            user_id, page_number, page_size, sorted
        )

        logger.info(f"Получено {len(reviews)} рецензий пользователя {user_id=}")

        if reviews:
            convert_review = [ReviewDetailResponse(**obj.model_dump()) for obj in reviews]
            await self.cache.background_set(
                key=cache_key,
                value=json.dumps([obj.model_dump(mode="json") for obj in convert_review]),
                expire=app_config.cache_expire_in_seconds,
            )
            return convert_review
        return []

    async def rate_review(
        self, review_id: UUID, user_id: UUID, mark: LikeEnum
    ) -> ReviewRateResponse:
        """
        Устанавливает или обновляет оценку (лайк или дизлайк) пользователя для рецензии.

        Args:
            review_id (UUID): Идентификатор рецензии, которую оценивает пользователь.
            user_id (UUID): Идентификатор пользователя, ставящего оценку.
            mark (LikeEnum): Тип оценки (LIKE или DISLIKE).

        Returns:
            ReviewRateResponse: Объект ответа, содержащий информацию об установленной оценке.
        """
        is_like = True
        if mark == LikeEnum.DISLIKE:
            is_like = False

        review_like_model = await self.review_like_repository.upsert(
            ReviewLike.user_id == user_id,
            ReviewLike.review_id == review_id,
            user_id=user_id,
            review_id=review_id,
            is_like=is_like,
        )
        logger.info(f"Пользователь {user_id=} оценил рецензию {review_id=} тип оценки {is_like=}")
        return ReviewRateResponse(**review_like_model.model_dump())

    async def delete_rate_review(self, user_id: UUID, review_id: UUID) -> None:
        """
        Удаляет оценку (лайк/дизлайк) пользователя для указанной рецензии.

        Args:
            user_id (UUID): Идентификатор пользователя, чья оценка удаляется.
            review_id (UUID): Идентификатор рецензии, с которой удаляется оценка.

        Returns:
            None: Метод не возвращает значений.
        """

        del_status = await self.review_like_repository.delete_document(
            ReviewLike.user_id == user_id,
            ReviewLike.review_id == review_id,
        )

        if not del_status:
            logger.warning(
                f"Оценка рецензии {review_id=} от пользователя {user_id=} не удалена или не найдена"
            )

        logger.info(f"Оценка пользователя {user_id=} удалена с рецензии {review_id}")


@lru_cache()
def get_review_service(
    cache: Annotated[Cache, Depends(get_cache)],
    review_repository: Annotated[ReviewRepository, Depends(get_review_repository)],
    review_like_repository: Annotated[ReviewLikeRepository, Depends(get_review_like_repository)],
    film_validator: Annotated[FilmIdValidator, Depends(get_film_id_validator)],
) -> ReviewService:
    return ReviewService(cache, review_repository, review_like_repository, film_validator)
