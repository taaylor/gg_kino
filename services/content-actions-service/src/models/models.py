from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

import pymongo
from beanie import Document, Indexed
from core.config import app_config
from pydantic import Field


class Like(Document):
    id: UUID = Field(default_factory=uuid4)  # Уникальный идентификатор лайка
    user_id: Annotated[UUID, Indexed(index_type=pymongo.ASCENDING)]
    film_id: Annotated[UUID, Indexed(index_type=pymongo.HASHED)]  # индекс для шардирования
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )  # Время создания

    class Settings:
        name = app_config.mongodb.like_coll


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
