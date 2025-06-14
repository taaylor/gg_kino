from uuid import UUID

from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    score: int = Field(
        ...,
        ge=1,
        le=10,
        description="Оценка фильма от 1 до 10.",
    )


class ScoreResponse(BaseModel):
    pass


class OutputRating(BaseModel):
    film_id: UUID = Field(..., alias="_id")
    rating: float = Field(..., alias="avg_rating")
    count_votes: int
