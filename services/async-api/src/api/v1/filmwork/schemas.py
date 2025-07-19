from enum import StrEnum
from uuid import UUID

from core.config import app_config
from fastapi import HTTPException, status
from models.schemas_logic import FilmLogic, GenreLogic, PersonLogic
from pydantic import BaseModel, Field, field_validator


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


class SearchByVectorsRequest(BaseModel):
    vectors: list[float] = Field(
        ...,
        description=(
            "Векторы для поиска фильма, количество"
            f" должно быть ровно {app_config.embedding_dims}."
        ),
    )

    @field_validator("vectors")
    @classmethod
    def validator_vectors(cls, vectors: list[float]):
        if len(vectors) != app_config.embedding_dims:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Количество векторов должно равняться {app_config.embedding_dims},"
                    f" пришло {len(vectors)}."
                ),
            )
        return vectors


class SearchByVectorsResponse(BaseModel):
    # TODO: временная схема, потом поменять на то чтобы отдавала весь фильм
    uuid: UUID = Field(..., description="Уникальный идентификатор фильма.")
    vectors: list[float] = Field(
        ...,
        description=(
            "Векторы для поиска фильма, количество"
            f" должно быть ровно {app_config.embedding_dims}."
        ),
    )
