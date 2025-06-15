from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class AvgRatingSchema(BaseModel):
    film_id: UUID = Field(..., alias="_id")
    rating: float = Field(..., alias="avg_rating")
    count_votes: int

    @field_validator("rating")
    def round_rating(cls, rating: float) -> float:
        return round(rating, 2)
