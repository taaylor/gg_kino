from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MixinTextField(BaseModel):
    text: str = Field(..., description="Текст рецензии добавленый пользователем")


class MixinTimestamp(BaseModel):
    updated_at: datetime = Field(..., description="Дата редактирования рецензии")
    created_at: datetime = Field(..., description="Дата создания рецензии")


class MixinReviewUUID(BaseModel):
    id: UUID = Field(..., description="Идентификатор рецензии")
    film_id: UUID = Field(..., description="Идентификатор фильма")
    user_id: UUID = Field(..., description="Автор рецензии")


class ReviewDetailResponse(MixinReviewUUID, MixinTextField, MixinTimestamp):
    user_score: float | None = Field(..., description="Оценка пользователя привязанная к фильму")
    count_like: int = Field(..., description="Количесвто лайков рецензии")
    count_dislike: int = Field(..., description="Количество дизлайков рецензии")


class ReviewModifiedResponse(MixinReviewUUID, MixinTextField, MixinTimestamp):
    """Модель ответа добавления/изменения рецензии"""


class ReviewModifiedRequest(MixinTextField):
    """Модель запроса добавления/изменения рецензии"""
