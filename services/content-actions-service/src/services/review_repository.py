import logging
from collections import defaultdict
from functools import lru_cache
from uuid import UUID

from beanie.operators import In
from models.enum_models import SortedEnum
from models.logic_models import ReviewSchema
from models.models import Rating, Review, ReviewLike
from services.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ReviewRepository(BaseRepository):

    __slots__ = ("collection",)

    async def get_reviews(  # noqa: WPS210
        self, film_id: UUID, page_number: int, page_size: int, sorted: SortedEnum
    ) -> list[ReviewSchema]:

        # получаем рецензии связанные с фильмом
        reviews = await self.find(
            Review.film_id == film_id,
            page_size=page_size,
            skip_page=page_number - 1,
            sorted=sorted,
        )
        logger.debug(f"Получено {len(reviews)} рецензий по фильму {film_id=} из хранилища")

        ids_users = []
        ids_reviews = []

        for review in reviews:
            ids_users.append(review.user_id)
            ids_reviews.append(review.id)

        # Получаем лайки рецензий
        reviews_like = await ReviewLike.find(In(ReviewLike.review_id, ids_reviews)).to_list()
        logger.debug(f"Получено {len(reviews_like)} оценки рецензий фильма {film_id=} из хранилища")

        # получаем оценки пользователей к рецензиям
        users_score = await Rating.find(
            Rating.film_id == film_id, In(Rating.user_id, ids_users)
        ).to_list()
        logger.debug(
            f"Получено {len(users_score)} оценок пользователей к рецензиям по \
                фильму {film_id=} из хранилища"
        )

        storage_users_score = {score.user_id: score.score for score in users_score}

        storage_like = defaultdict(list)
        for review in reviews_like:
            storage_like[review.review_id].append(review.is_like)

        results = []
        for review in reviews:
            cnt_like = 0
            cnt_dislike = 0
            for lik in storage_like.get(review.id, []):

                if lik is True:
                    cnt_like += 1
                elif lik is False:
                    cnt_dislike += 1

            score = storage_users_score.get(review.user_id, None)
            results.append(
                ReviewSchema(
                    id=review.id,
                    film_id=film_id,
                    user_id=review.user_id,
                    text=review.text,
                    user_score=score,
                    count_like=cnt_like,
                    count_dislike=cnt_dislike,
                    created_at=review.created_at,
                    updated_at=review.updated_at,
                )
            )
        logger.debug(f"Получено и обработано {len(results)} рецензий к фильму {film_id=}")

        return results


class ReviewLikeRepository(BaseRepository):
    __slots__ = ("collection",)


@lru_cache()
def get_review_repository() -> ReviewRepository:
    return ReviewRepository(Review)


@lru_cache()
def get_review_like_repository() -> ReviewLikeRepository:
    return ReviewLikeRepository(ReviewLike)
