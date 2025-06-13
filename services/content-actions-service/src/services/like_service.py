# import json
import logging

# from functools import lru_cache
from uuid import UUID

# from core.config import app_config
# from fastapi import Depends, HTTPException, status
from services.like_repository import RatingRepository

logger = logging.getLogger(__name__)

CACHE_KEY_AVG_RATING = "films:avg_rating:"


class RatingService:

    def __init__(
        self,
        # cache: Cache,
        repository: RatingRepository,
    ):
        # self.cache = cache
        self.repository = repository

    async def get_average_rating(self, film_id: UUID):
        """Возвращает список всех ролей с базовой информацией"""
        cache_key = f"{CACHE_KEY_AVG_RATING}:{str(film_id)}"
        avg_rating = None  # await self.cache.get(cache_key)

        if avg_rating:
            logger.debug(f"Средний арифметический рейтинг фильма получен из кеша: {avg_rating}")
            cache_key
            # return [RoleResponse.model_validate(r) for r in json.loads(role_cache)]
            return "something"

        avg_rating = await self.repository.calculate_average_rating(
            self.repository.collection.film_id == film_id
        )

        if not avg_rating:
            return None
        result = avg_rating[0].model_dump()
        # await self.cache.background_set(
        #     key=cache_key, value=result, expire=app_config.cache_expire_in_seconds
        # )
        return result

    async def set_user_score(self, user_id: UUID, film_id: UUID, rating: int):
        result = await self.repository.upsert(
            self.repository.collection.user_id == user_id,
            self.repository.collection.film_id == film_id,
            update_fields=[
                "rating",
            ],
            # update_fields=["rating", "lalala"],
            # update_fields=[],
            user_id=user_id,
            film_id=film_id,
            rating=rating,
        )
        """
        {
            "_id": "4cf5009a-c832-4e0e-b334-cd6109754921",
            "user_id": "5580dfe4-9803-4291-8e6b-6e7df27d7032",
            "film_id": "cd4225d4-8087-4a42-aaf7-30a30e8a919d",
            "created_at": "2025-06-13T18:35:41.593461Z",
            "updated_at": "2025-06-13T18:35:41.593464Z",
            "rating": 6
        }
        """
        return result

    async def delete_user_score(self, user_id: UUID, film_id: UUID):
        await self.repository.delete_document(
            self.repository.collection.user_id == user_id,
            self.repository.collection.film_id == film_id,
        )


# @lru_cache()
# def get_rating_service(
#     # cache: Cache = Depends(get_cache),
#     repository: RatingRepository = RatingRepository,
# ) -> RatingService:
#     return RatingService(
#         # cache,
#         repository
#     )
