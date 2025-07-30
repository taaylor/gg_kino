from typing import Annotated

from core.config import app_config
from pydantic import BaseModel, BeforeValidator, Field


def set_default_imdb_rating(value: float | None) -> float:
    if isinstance(value, (float, int)):
        if value >= app_config.high_rating_level:
            return "High rating."
    return ""


def set_genres_as_str(genres: list[str]) -> str:
    if genres and isinstance(genres, list):
        return ", ".join(genres)
    return ""


def set_description_as_str(description: str | None) -> str:
    if description is None:
        return ""
    return description


class FilmLogic(BaseModel):
    id: Annotated[str, Field(description="Уникальный идентификатор фильма")]
    title: Annotated[str, Field(description="Название фильма")]
    description: Annotated[
        str,
        Field(description="Название фильма"),
        BeforeValidator(set_description_as_str),
    ]
    imdb_rating: Annotated[
        str,
        Field(description="Рейтинг фильма на IMDB"),
        BeforeValidator(set_default_imdb_rating),
    ]
    genres_names: Annotated[
        str,
        Field(description="Жанры фильма"),
        BeforeValidator(set_genres_as_str),
    ]


class EmbeddedFilm(BaseModel):
    id: Annotated[str, Field(description="Уникальный идентификатор фильма")]
    embedding: Annotated[
        list[float],
        Field(
            description=(
                "Вектор для поиска фильма, количество"
                f" должно быть ровно {app_config.embedding_dims}."
            )
        ),
    ]
