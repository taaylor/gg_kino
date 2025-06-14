import logging
from functools import lru_cache
from typing import Any

from models.logic_models import AvgRatingSchema
from models.models import Rating
from services.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class RatingRepository(BaseRepository):

    async def calculate_average_rating(self, *filters: Any) -> AvgRatingSchema | None:
        document = (
            await self.collection.find(*filters)
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
                projection_model=AvgRatingSchema,
            )
            .to_list()
        )
        if not document:
            return None
        return document


@lru_cache()
def get_rating_repository() -> RatingRepository:
    return RatingRepository(Rating)
