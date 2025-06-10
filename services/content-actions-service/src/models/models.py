from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

import pymongo
from beanie import Document, Indexed
from pydantic import Field


class Like(Document):
    id: UUID = Field(default_factory=uuid4)  # Уникальный идентификатор лайка
    user_id: Annotated[UUID, Indexed(index_type=pymongo.ASCENDING)]
    film_id: Annotated[UUID, Indexed(index_type=pymongo.HASHED)]  # индекс для шардирования
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )  # Время создания

    class Settings:
        name = "likeCollection"


class Review(Document):
    id: UUID = Field(default_factory=uuid4)  # Уникальный идентификатор лайка
    user_id: Annotated[UUID, Indexed(index_type=pymongo.ASCENDING)]
    film_id: Annotated[UUID, Indexed(index_type=pymongo.HASHED)]  # индекс для шардирования
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )  # Время создания

    class Settings:
        name = "reviewsCollection"


class Bookmark(Document):
    id: UUID = Field(default_factory=uuid4)  # Уникальный идентификатор лайка
    user_id: Annotated[UUID, Indexed(index_type=pymongo.ASCENDING)]
    film_id: Annotated[UUID, Indexed(index_type=pymongo.HASHED)]  # индекс для шардирования
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )  # Время создания

    class Settings:
        name = "bookmarkCollection"
