from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pymongo
from beanie import Document
from core.config import app_config
from models.enum_models import FilmBookmarkState
from pydantic import Field


class TimestampMixin(Document):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Документ создан",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Документ обновлён",
    )


class BaseDocument(TimestampMixin):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID = Field(
        ...,
        description="user_id документа",
    )
    film_id: UUID = Field(
        ...,
        description="film_id документа, (ключ шардирования)",
    )


class Rating(BaseDocument):
    score: int = Field(..., description="Оценка фильма от 1 до 10.")

    class Settings:
        name = app_config.mongodb.like_coll
        indexes = [
            pymongo.IndexModel(
                [
                    ("film_id", pymongo.ASCENDING),
                    ("user_id", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]


class Review(BaseDocument):
    text: str = Field(
        ..., description="Текст рецензии", min_length=5, max_length=500  # noqa: WPS432
    )

    class Settings:
        name = app_config.mongodb.reviews_coll
        use_revision = False
        indexes = [
            pymongo.IndexModel([("film_id", pymongo.ASCENDING)]),
            pymongo.IndexModel([("created_at", pymongo.ASCENDING)]),
        ]


class ReviewLike(TimestampMixin):
    is_like: bool = Field(
        ..., description="Оценка рецензии пользователем True = лайк, False = дизлайк"
    )
    review_id: UUID = Field(..., description="Идентификатор рецензии")
    author_user_id: UUID = Field(..., description="Идентификатор пользователя автора рецензии")
    film_id: UUID = Field(..., description="Идентификатор фильма, на который было ревью")
    user_id: UUID = Field(..., description="Идентификатор пользователя")

    class Settings:
        # позволяет включить кеширование заросов на уровне lru_cache
        # первый запрос будет в бд, второй будет браться из кеша
        use_cache = True
        cache_expiration_time = timedelta(seconds=10)
        cache_capacity = 5

        name = app_config.mongodb.reviews_like_coll
        use_revision = False
        indexes = [
            pymongo.IndexModel(
                [
                    ("review_id", pymongo.ASCENDING),
                    ("user_id", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]


class Bookmark(BaseDocument):
    comment: str | None = Field(
        None,
        min_length=5,
        max_length=500,  # noqa: WPS432
    )
    status: FilmBookmarkState = Field(FilmBookmarkState.NOTWATCHED)

    class Settings:
        name = app_config.mongodb.bookmark_coll
        indexes = [
            pymongo.IndexModel(
                [
                    ("film_id", pymongo.ASCENDING),
                    ("user_id", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]
