from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ScoreRequest(BaseModel):
    score: int = Field(
        ...,
        ge=1,
        le=10,
        description="Оценка фильма от 1 до 10.",
    )


class ScoreResponse(BaseModel):
    user_id: UUID = Field(..., description="id пользователя поставившего оценку")
    film_id: UUID = Field(..., description="id фильма поставившего оценку")
    created_at: datetime = Field(..., description="Время создания документа")
    updated_at: datetime = Field(..., description="Время обновления документа")
    score: float = Field(..., description="Оценка фильма")

    """
    {
        "_id": "49602e24-babd-4e33-87b6-fe918edbc68e",
        "user_id": "d75589b0-0318-4360-b07a-88944c24bd92",
        "film_id": "4547b202-5f72-4c5e-ae79-9c46f3f95037",
        "created_at": "2025-06-14T15:21:30.319215Z",
        "updated_at": "2025-06-14T15:21:30.319219Z",
        "score": 9
    }
    """
    pass


class AvgRatingResponse(BaseModel):
    film_id: UUID = Field(..., description="id пользователя поставившего оценку")
    rating: float = Field(..., description="Средняя оценка фильма")
    count_votes: int = Field(..., description="Количество оценивших")

    @field_validator("rating")
    def round_rating(cls, value: float) -> float:
        return round(value, 2)
