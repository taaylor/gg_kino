from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FilmListSchema(BaseModel):
    """Схема для ответа API, представляющая полную информацию о фильме."""

    film_id: UUID = Field(
        ...,
        description="Уникальный идентификатор фильма.",
    )
    film_title: str = Field(
        ...,
        description="Название фильма.",
    )
    imdb_rating: float | None = Field(
        None,
        description="Рейтинг фильма по версии IMDB.",
    )


class RecomendedFilmsSchema(BaseModel):
    recommended_films: list[FilmListSchema] = Field(
        default_factory=list,
        description="Список жанров фильма.",
    )


class RegularMassSendingSchemaRequest(BaseModel):
    target_start_sending_at: datetime = Field(
        ...,
        description="Данные о событиях и рекомендациях",
    )
    event_data: RecomendedFilmsSchema = Field(
        ...,
        description="Данные о событиях и рекомендациях",
    )
    template_id: UUID = Field(
        ...,
        description="UUID шаблона",
    )


class ResponseToMassNotificationSchema(BaseModel):
    target_start_sending_at: datetime = Field(
        ...,
        description="Начало запуска рассылки",
    )
    event_data: RecomendedFilmsSchema = Field(
        ...,
        description="Список рекомендуемых фильмов.",
    )
    template_id: UUID = Field(
        ...,
        description="UUID шаблона для email.",
    )
