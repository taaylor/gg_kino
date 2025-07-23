from uuid import UUID

from pydantic import BaseModel


class LlmResponse(BaseModel):
    genre: str | None = None
    theme: str | None = None
    has_genre: bool = False
    has_theme: bool = False
    genres_scores: float = 0
    theme_scores: float = 0
    status: str


class FilmListResponse(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float | None
    type: str


class GenreResponse(BaseModel):
    uuid: UUID
    name: str
