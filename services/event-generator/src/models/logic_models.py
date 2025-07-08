from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class FilmsType(StrEnum):
    FREE = "FREE"
    PAID = "PAID"
    ARCHIVED = "ARCHIVED"


class FilmListSchemaRequest(BaseModel):
    film_id: str = Field(..., description="Уникальный идентификатор фильма.")


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
    # genre: list[GenreLogic] = Field(
    #     default_factory=list,
    #     description="Список жанров фильма.",
    # )
    # @classmethod
    # def transform_from_FilmLogic(cls, film: FilmLogic) -> "FilmInternalResponse":
    #     return cls(
    #         uuid=film.id,
    #         title=film.title,
    #         description=film.description,
    #         imdb_rating=film.imdb_rating,
    #         genre=film.genres,
    #         directors=film.directors,
    #         actors=film.actors,
    #         writers=film.writers,
    #         type=film.type,
    #     )


"""
  {
    "uuid": "3aba7aa0-8930-417c-bf78-3df596c3f062",
    "title": "Star Wars: The Old Republic",
    "imdb_rating": 8.7,
    "type": "FREE"
  }
]

{
  "target_start_sending_at": "2025-07-08: 20:20:20",
  "event_data": {
    "recommended_films": [
      {
        "film_id": "uuid",
        "film_title": "Горбатая гора",
        "imbd_raiting": 10
      }
    ]
  },
  "template_id": "uuid"
}

"""
