from datetime import datetime, timezone
from uuid import UUID, uuid4

import pymongo
from beanie import Document
from core.config import app_config
from models.logic_models import FilmBookmarkState
from pydantic import Field


class BaseDocument(Document):
    id: UUID = Field(default_factory=uuid4)  # type: ignore
    user_id: UUID = Field(
        ...,
        description="user_id документа",
    )  # Indexed ниже через Settings.indexes
    film_id: UUID = Field(
        ...,
        description="film_id документа, (ключ шардирования)",
    )  # Indexed ниже через Settings.indexes
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Документ создан",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Документ обновлён",
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

    class Settings:
        name = app_config.mongodb.reviews_coll


class Bookmark(BaseDocument):
    comment: str | None = Field(
        None,
        min_length=5,
        max_length=500,
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
