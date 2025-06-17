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
        examples=["Звучит хайпово, посмотрю на НГ"],
        description="Опциональный комментарий к фильму в закладках",
    )


class StatusField(BaseModel):
    status: FilmBookmarkState = Field(
        FilmBookmarkState.NOTWATCHED, description="Статус просмотра фильма в закладках"
    )


class BookmarkObj(FilmIdField, DateFields, CommentField, StatusField):
    pass


class WatchListPage(BaseModel):
    count_total: int = Field(..., description="Общее количество фильмов в списке для просмотра")
    count_on_page: int = Field(
        ..., description="Количество фильмов в списке для просмотра на текущей странице"
    )
    watchlist_page: list[BookmarkObj] = Field(
        ..., description="Список фильмов в закладках у пользователя"
    )


class CreateBookmarkRequest(CommentField):
    pass


class CreateBookmarkResponse(BookmarkObj):
    pass


class FetchBookmarkList(WatchListPage):
    user_id: UUID = Field(
        ..., description="Идентификатор пользователя, которому принадлежит список закладок"
    )


class ChangeBookmarkRequest(CommentField, StatusField):
    pass


class ChangeBookmarkResponse(BookmarkObj):
    pass
