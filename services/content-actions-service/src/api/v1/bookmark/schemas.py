from datetime import datetime
from uuid import UUID

from models.logic_models import FilmBookmarkState
from pydantic import BaseModel, Field


class FilmIdField(BaseModel):
    film_id: UUID = Field(..., description="Уникальный идентификатор фильма")


class DateFields(BaseModel):
    created_at: datetime = Field(..., description="Дата создания записи")
    updated_at: datetime = Field(..., description="Дата обновления записи")


class CommentField(BaseModel):
    comment: str | None = Field(
        None,
        min_length=5,
        max_length=500,
        description="Опциональный комментарий к фильму в закладках",
    )


class BookmarkObj(FilmIdField, DateFields, CommentField):
    status: FilmBookmarkState = Field(
        FilmBookmarkState.NOTWATCHED, description="Статус просмотра фильма в закладках"
    )


class CreateBookmarkRequest(CommentField):
    pass


class CreateBookmarkResponse(FilmIdField, CommentField, DateFields):
    pass


class FetchBookmarkList(BaseModel):
    user_id: UUID = Field(
        ..., description="Идентификатор пользователя, которому принадлежит список закладок"
    )
    watchlist: list[BookmarkObj] = Field(
        ..., description="Список фильмов в закладках у пользователя"
    )


class ChangeBookmarkResponse(BookmarkObj):
    pass
