# from datetime import datetime, timezone
import logging

from api.v1.rating.schemas import OutputRating

# from fastapi import HTTPException, status
from models.models import Rating
from services.base_repository import BaseRepository

# from functools import lru_cache

# from beanie import Document


logger = logging.getLogger(__name__)


class RatingRepository(BaseRepository):

    collection = Rating

    @classmethod
    async def calculate_average_rating(cls, *filters):
        document = (
            await cls.collection.find(*filters)
            .aggregate(
                [
                    {
                        "$group": {
                            "_id": "$film_id",
                            "avg_rating": {"$avg": "$score"},
                            "count_votes": {"$sum": 1},
                        }
                    }
                ],
                projection_model=OutputRating,
            )
            .to_list()
        )
        if not document:
            return None
        return document
