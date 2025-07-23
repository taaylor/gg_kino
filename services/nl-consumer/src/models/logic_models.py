from uuid import UUID, uuid4

from pydantic import BaseModel, Field


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


class QueryModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    text: str
