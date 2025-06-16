from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class SortedReview(Enum):
    CREATED_ASC = "created_at"
    CREATED_DESC = "-created_at"
    LIKE_ASC = "like"


class ReviewResponse(BaseModel):
    id: UUID = Field(..., description="Идентификатор рецензии")
    film_id: UUID = Field(..., description="Идентификатор фильма")
    user_id: UUID = Field(..., description="Автор рецензии")
    text: str = Field(..., description="Текст рецензии")
    user_score: float = Field(..., description="Оценка фильма поставленная пользователем")
    like_review: int = Field(..., description="Количесвто лайков рецензии")
    dislike_review: int = Field(..., description="Количество дизлайков рецензии")
    created_at: datetime = Field(..., description="Дата создания рецензии")
    updated_at: datetime = Field(..., description="Дата редактирования рецензии")
