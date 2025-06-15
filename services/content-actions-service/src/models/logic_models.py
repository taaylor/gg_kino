from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class FilmBookmarkState(StrEnum):
    NOTWATCHED = "NOTWATCHED"
    WATCHED = "WATCHED"


class AvgRatingSchema(BaseModel):
    film_id: UUID = Field(..., alias="_id")
    rating: float = Field(..., alias="avg_rating")
    count_votes: int

    @field_validator("rating")
    def round_rating(cls, value: float) -> float:
        return round(value, 2)
