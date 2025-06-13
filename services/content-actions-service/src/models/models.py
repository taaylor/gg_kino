from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

import pymongo
from beanie import Document, Indexed
from core.config import app_config
from pydantic import Field


class Like(Document):
    id: UUID = Field(default_factory=uuid4)  # Уникальный идентификатор документа
    # user_id: Annotated[UUID, Indexed(index_type=pymongo.ASCENDING)]
    # film_id: Annotated[UUID, Indexed(index_type=pymongo.HASHED)]
    user_id: UUID = Field(
        ...,
        description="user_id документа",
    )  # Indexed ниже через Settings.indexes
    film_id: UUID = Field(
        ...,
        description="film_id документа, (ключ шардирования)",
    )  # Indexed ниже через Settings.indexes
    rating: int = Field(..., description="0 для дизлайка, 10 для лайка")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = app_config.mongodb.like_coll
        indexes = [
            # индекс для шардирования
            pymongo.IndexModel(
                [("film_id", pymongo.HASHED)],
            ),
            # pymongo.IndexModel(
            #     [("user_id", pymongo.ASCENDING)],
            # ),
            # уникальный составной индекс
            pymongo.IndexModel(
                [
                    ("film_id", pymongo.ASCENDING),
                    ("user_id", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]


class Review(Document):
    id: UUID = Field(default_factory=uuid4)  # Уникальный идентификатор лайка
    user_id: Annotated[UUID, Indexed(index_type=pymongo.ASCENDING)]
    film_id: Annotated[UUID, Indexed(index_type=pymongo.HASHED)]  # индекс для шардирования
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )  # Время создания

    class Settings:
        name = app_config.mongodb.reviews_coll


class Bookmark(Document):
    id: UUID = Field(default_factory=uuid4)  # Уникальный идентификатор лайка
    user_id: Annotated[UUID, Indexed(index_type=pymongo.ASCENDING)]
    film_id: Annotated[UUID, Indexed(index_type=pymongo.HASHED)]  # индекс для шардирования
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )  # Время создания

    class Settings:
        name = app_config.mongodb.bookmark_coll
