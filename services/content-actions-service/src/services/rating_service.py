import json
import logging
from functools import lru_cache
from uuid import UUID

from api.v1.rating.schemas import AvgRatingResponse, ScoreResponse
from core.config import app_config
from db.cache import Cache, get_cache
from fastapi import Depends
from services.rating_repository import RatingRepository, get_rating_repository

logger = logging.getLogger(__name__)

CACHE_KEY_AVG_RATING = "films:avg_rating:"


class RatingService:

    def __init__(
        self,
        cache: Cache,
        repository: RatingRepository,
    ):
        self.cache = cache
        self.repository = repository

    async def get_average_rating(self, film_id: UUID) -> AvgRatingResponse | None:
        """Возвращает список всех ролей с базовой информацией"""
        cache_key = CACHE_KEY_AVG_RATING + str(film_id)
        avg_rating = await self.cache.get(cache_key)

        if avg_rating:
            logger.debug(f"Средний арифметический рейтинг фильма получен из кеша: {avg_rating}")
            return AvgRatingResponse.model_validate(json.loads(avg_rating))

        avg_rating = await self.repository.calculate_average_rating(
            self.repository.collection.film_id == film_id
        )

        if not avg_rating:
            return None
        result = avg_rating[0].model_dump()
        await self.cache.background_set(
            key=cache_key, value=result, expire=app_config.cache_expire_in_seconds
        )
        return AvgRatingResponse(**result)

    async def set_user_score(self, user_id: UUID, film_id: UUID, score: int) -> ScoreResponse:
        document = await self.repository.upsert(
            self.repository.collection.user_id == user_id,
            self.repository.collection.film_id == film_id,
            user_id=user_id,
            film_id=film_id,
            score=score,
        )
        result = ScoreResponse(
            user_id=document.user_id,
            film_id=document.film_id,
            created_at=document.created_at,
            updated_at=document.updated_at,
            score=document.score,
        )
        return result

    async def delete_user_score(self, user_id: UUID, film_id: UUID) -> None:
        await self.repository.delete_document(
            self.repository.collection.user_id == user_id,
            self.repository.collection.film_id == film_id,
        )


@lru_cache()
def get_rating_service(
    cache: Cache = Depends(get_cache),
    repository: RatingRepository = Depends(get_rating_repository),
) -> RatingService:
    return RatingService(cache, repository)
