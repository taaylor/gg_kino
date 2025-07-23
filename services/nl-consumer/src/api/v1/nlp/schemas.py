from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class Film(BaseModel):
    uuid: Annotated[UUID, Field(description="Уникальный идентификатор фильма")]
    title: Annotated[str, Field(description="Название фильма")]
    imdb_rating: Annotated[float | None, Field(description="Рейтинг фильма на IMDB")]
    type: Annotated[str, Field(description="Тип фильма (Платный, Бесплатный...)")]


class RecsRequest(BaseModel):
    query: Annotated[
        str,
        Field(
            ..., min_length=10, max_length=500, description="Пользовательский запрос рекомендации"
        ),
    ]


class RecsResponse(BaseModel):
    films: Annotated[list[Film] | None, Field(description="Список рекомендуемых фильмов")]
    message: Annotated[str | None, Field(description="Сообщение с результатом выбора фильма")]
