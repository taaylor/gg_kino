from enum import StrEnum
from uuid import UUID

from models.schemas_logic import FilmLogic, GenreLogic, PersonLogic
from pydantic import BaseModel, Field


class FilmsType(StrEnum):
    FREE = "FREE"
    PAID = "PAID"
    ARCHIVED = "ARCHIVED"


class FilmDetailResponse(BaseModel):
    """Схема для ответа API, представляющая полную информацию о фильме."""

    uuid: UUID = Field(
        ...,
        description="Уникальный идентификатор фильма.",
    )
    title: str = Field(
        ...,
        description="Название фильма.",
    )
    imdb_rating: float | None = Field(
        None,
        description="Рейтинг фильма по версии IMDB.",
    )
    description: str | None = Field(
        None,
        description="Описание фильма.",
    )
    genre: list[GenreLogic] = Field(
        default_factory=list,
        description="Список жанров фильма.",
    )
    actors: list[PersonLogic] = Field(
        default_factory=list,
        description="Список актеров фильма.",
    )
    writers: list[PersonLogic] = Field(
        default_factory=list,
        description="Список сценаристов фильма.",
    )
    directors: list[PersonLogic] = Field(
        default_factory=list,
        description="Список режиссеров фильма.",
    )
    type: FilmsType = Field(..., description="Тип фильма")

    @classmethod
    def transform_from_FilmLogic(cls, film: FilmLogic) -> "FilmDetailResponse":
        return cls(
            uuid=film.id,
            title=film.title,
            description=film.description,
            imdb_rating=film.imdb_rating,
            genre=film.genres,
            directors=film.directors,
            actors=film.actors,
            writers=film.writers,
            type=film.type,
        )


class FilmListResponse(BaseModel):
    """Схема для ответа API, представляющая сокращенную информацию о фильмах."""

    uuid: UUID = Field(..., description="Уникальный идентификатор фильма.")
    title: str = Field(
        ...,
        description="Название фильма.",
    )
    imdb_rating: float | None = Field(
        None,
        description="Рейтинг фильма по версии IMDB. Может отсутствовать.",
    )
    type: FilmsType = Field(..., description="Тип фильма")


class FilmSorted(StrEnum):
    RATING_DESC = "-imdb_rating"
    RATING_ASC = "imdb_rating"

    def __str__(self):
        return self.value


class FilmRecResponse(BaseModel):
    film_recommended: list[FilmListResponse] = Field(
        default_factory=list,
        description="Персональные рекомендации пользователя",
    )
    film_trend: list[FilmListResponse] = Field(
        default_factory=list, description="Фильмы которые в тренде"
    )
