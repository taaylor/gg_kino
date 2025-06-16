from functools import lru_cache
from typing import Annotated

from db.cache import Cache, get_cache
from fastapi import Depends
from services.review_repository import (
    ReviewLikeRepository,
    ReviewRepository,
    get_review_like_repository,
    get_review_repository,
)


class ReviewService:

    __slots__ = ("cache", "review_repository", "review_like_repository")

    def __init__(
        self,
        cache: Cache,
        review_repository: ReviewRepository,
        review_like_repository: ReviewLikeRepository,
    ):
        self.cache = cache
        self.review_repository = review_repository
        self.review_like_repository = review_like_repository


@lru_cache()
def get_review_service(
    cache: Annotated[Cache, Depends(get_cache)],
    review_repository: Annotated[ReviewRepository, Depends(get_review_repository)],
    review_like_repository: Annotated[ReviewLikeRepository, Depends(get_review_like_repository)],
) -> ReviewService:
    return ReviewService(cache, review_repository, review_like_repository)
