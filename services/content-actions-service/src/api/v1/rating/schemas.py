from datetime import datetime
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
    user_id: UUID = Field(..., description="id пользователя поставившего оценку")
    film_id: UUID = Field(..., description="id фильма поставившего оценку")
    created_at: datetime = Field(..., description="Время создания документа")
    updated_at: datetime = Field(..., description="Время обновления документа")
    score: float = Field(..., description="Оценка фильма")


class AvgRatingResponse(BaseModel):
    film_id: UUID = Field(..., description="id пользователя поставившего оценку")
    rating: float = Field(..., description="Средняя оценка фильма")
    count_votes: int = Field(..., description="Количество оценивших")
    user_score: int | None
