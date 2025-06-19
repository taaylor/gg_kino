from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class AvgRatingSchema(BaseModel):
    film_id: UUID = Field(..., alias="_id")
    rating: float = Field(..., alias="avg_rating")
    count_votes: int

    @field_validator("rating")
    def round_rating(cls, rating: float) -> float:
        return round(rating, 2)


class ReviewRepositorySchema(BaseModel):
    id: UUID = Field(alias="_id")
    film_id: UUID
    user_id: UUID
    text: str
    like_count: int
    dislike_count: int
    created_at: datetime
    updated_at: datetime


class ReviewScoreSchema(ReviewRepositorySchema):
    user_score: int | None
