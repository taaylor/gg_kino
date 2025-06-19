import logging
from functools import lru_cache
from typing import Any
from uuid import UUID

import backoff
from beanie.operators import In
from core.config import app_config
from models.enum_models import SortedEnum
from models.logic_models import ReviewRepositorySchema, ReviewScoreSchema
from models.models import Rating, Review, ReviewLike
from services.base_repository import BaseRepository
from utils.decorators import mongodb_handler_exceptions

logger = logging.getLogger(__name__)


class ReviewRepository(BaseRepository[Review]):
    """Репозиторий для работы рецензиями"""

    __slots__ = ("collection",)

    @backoff.on_exception(backoff.expo, app_config.mongodb.base_connect_exp)
    @mongodb_handler_exceptions
    async def get_reviews(
        self, film_id: UUID, page_number: int, page_size: int, sorted: SortedEnum
    ) -> list[ReviewScoreSchema]:
        """
        Получает список рецензий для фильма с пагинацией и сортировкой.

        Метод выполняет агрегацию в MongoDB для получения рецензий по указанному фильму,
        подсчитывает лайки и дизлайки, а также присоединяет оценки пользователей к рецензиям.

        Args:
            film_id (UUID): Уникальный идентификатор фильма, для которого запрашиваются рецензии.
            page_number (int): Номер страницы для пагинации (начиная с 1).
            page_size (int): Количество рецензий на одной странице.
            sorted (SortedEnum): Порядок сортировки рецензий (например, по дате или рейтингу).

        Returns:
            list[ReviewScoreSchema]: Список рецензий с данными о лайках,
            дизлайках и оценках пользователей.

        Notes:
            - Декоратор `@backoff.on_exception` автоматически повторяет попытки выполнения запроса
            при возникновении ошибок подключения или сетевых таймаутов.
            - Метод использует агрегационный пайплайн MongoDB для фильтрации рецензий по `film_id`,
            применения пагинации и сортировки.
            - Оценки пользователей запрашиваются отдельно через модель `Rating`
            и добавляются к результату.
        """

        # получаем pipeline для агрегации и выполняем запрос
        pipeline = self._get_pipline(
            {"film_id": film_id},
            skip=(page_number - 1) * page_size,
            page_size=page_size,
            sorted=sorted,
        )
        reviews = await self.collection.aggregate(
            pipeline, projection_model=ReviewRepositorySchema
        ).to_list()
        logger.debug(f"Получено {len(reviews)} рецензий по фильму {film_id=} из хранилища")

        # получаем оценки пользователей к рецензиям
        users_score = await Rating.find(
            Rating.film_id == film_id, In(Rating.user_id, [rev.user_id for rev in reviews])
        ).to_list()
        logger.debug(
            f"Получено {len(users_score)} оценок пользователей к рецензиям по \
                фильму {film_id=} из хранилища"
        )

        storage_users_score = {score.user_id: score.score for score in users_score}
        return self._conversion_to_reviews(reviews, storage_users_score, "user_id")

    @backoff.on_exception(backoff.expo, app_config.mongodb.base_connect_exp)
    @mongodb_handler_exceptions
    async def get_user_reviews(
        self, user_id: UUID, page_number: int, page_size: int, sorted: SortedEnum
    ) -> list[ReviewScoreSchema]:
        """
        Получает рецензии пользователя с пагинацией и сортировкой.

        Метод выполняет агрегацию в MongoDB (подсчет лайков и дизлайков) для получения
        рецензий по указанному пользователю, а также запрашивает оценки пользователя для фильмов,
        упомянутых в рецензиях. Данные преобразуются в объекты ReviewScoreSchema.

        Args:
            user_id (UUID): Идентификатор пользователя.
            page_number (int): Номер страницы для пагинации.
            page_size (int): Количество элементов на странице.
            sorted (SortedEnum): Порядок сортировки.

        Returns:
            list[ReviewScoreSchema]: Список рецензий с оценками.

        Notes:
            - Декоратор `@backoff.on_exception` автоматически повторяет попытки выполнения запроса
            при возникновении ошибок подключения или сетевых таймаутов.
            - Метод использует агрегационный пайплайн MongoDB для фильтрации рецензий по `user_id`,
            применения пагинации и сортировки.
            - Оценка пользователя запрашиваются отдельно через модель `Rating`
            и добавляются к результату.
        """

        # получаем pipeline для агрегации и выполняем запрос
        pipeline = self._get_pipline(
            {"user_id": user_id},
            skip=(page_number - 1) * page_size,
            page_size=page_size,
            sorted=sorted,
        )
        reviews = await self.collection.aggregate(
            pipeline, projection_model=ReviewRepositorySchema
        ).to_list()
        logger.debug(f"Получено {len(reviews)} рецензий пользователя {user_id=} из хранилища")

        # получаем оценки фильмов пользователя
        user_scores = await Rating.find(
            Rating.user_id == user_id, In(Rating.film_id, [rev.film_id for rev in reviews])
        ).to_list()
        logger.debug(
            f"Получено {len(user_scores)} оценок пользователя {user_id=} к фильмам из хранилища"
        )

        storage_rating_film = {score.film_id: score.score for score in user_scores}

        return self._conversion_to_reviews(reviews, storage_rating_film, "film_id")

    @staticmethod
    def _conversion_to_reviews(  # noqa: WPS602
        reviews: list[ReviewRepositorySchema], storage_rating: dict[str, int], key_rating: str
    ) -> list[ReviewScoreSchema]:
        """
        Статический метод который приводит к общему виду полученные из репозитория рецензии,
        оценки(у) пользователя(ей).
        Возвращает список преобразованых рецензий.
        """

        results = []
        for review in reviews:
            score = storage_rating.get(getattr(review, key_rating), None)
            results.append(
                ReviewScoreSchema(
                    _id=review.id,
                    film_id=review.film_id,
                    user_id=review.user_id,
                    text=review.text,
                    user_score=score,
                    like_count=review.like_count,
                    dislike_count=review.dislike_count,
                    created_at=review.created_at,
                    updated_at=review.updated_at,
                )
            )
        return results

    @staticmethod
    def _get_pipline(  # noqa: WPS602
        match: dict[str, Any], skip: int, page_size: int, sorted: SortedEnum
    ) -> list[dict[str, Any]]:
        """
        Возвращает pipeline для получения рецензий по условию и агрегации по лайкам
        """
        sort = {"created_at": -1}
        if sorted == SortedEnum.CREATED_ASC:
            sort = {"created_at": 1}

        return [
            {"$match": match},
            {
                "$lookup": {
                    "from": app_config.mongodb.reviews_like_coll,
                    "localField": "_id",
                    "foreignField": "review_id",
                    "as": "likes_data",
                }
            },
            {
                "$addFields": {
                    "like_count": {
                        "$size": {
                            "$filter": {
                                "input": "$likes_data",
                                "as": "like",
                                "cond": {"$eq": ["$$like.is_like", True]},
                            }
                        }
                    },
                    "dislike_count": {
                        "$size": {
                            "$filter": {
                                "input": "$likes_data",
                                "as": "like",
                                "cond": {"$eq": ["$$like.is_like", False]},
                            }
                        }
                    },
                }
            },
            {"$unset": "likes_data"},
            {"$sort": sort},
            {"$skip": skip},
            {"$limit": page_size},
        ]


class ReviewLikeRepository(BaseRepository[ReviewLike]):
    """Репозиторий для работы с лайками рецензий."""

    __slots__ = ("collection",)


@lru_cache()
def get_review_repository() -> ReviewRepository:
    return ReviewRepository(Review)


@lru_cache()
def get_review_like_repository() -> ReviewLikeRepository:
    return ReviewLikeRepository(ReviewLike)
