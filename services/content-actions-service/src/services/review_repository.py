import logging
from functools import lru_cache

from models.models import Review, ReviewLike
from services.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ReviewRepository(BaseRepository):

    __slots__ = ("collection",)


class ReviewLikeRepository(BaseRepository):

    __slots__ = ("collection",)


@lru_cache()
def get_review_repository() -> ReviewRepository:
    return ReviewRepository(Review)


@lru_cache()
def get_review_like_repository() -> ReviewLikeRepository:
    return ReviewLikeRepository(ReviewLike)
