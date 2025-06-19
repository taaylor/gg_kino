from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TextFieldMixin(BaseModel):
    text: str = Field(
        ...,
        description="Текст рецензии добавленый пользователем",
        min_length=5,
        max_length=500,  # noqa: WPS432
    )


class TimestampMixin(BaseModel):
    updated_at: datetime = Field(..., description="Дата редактирования рецензии")
    created_at: datetime = Field(..., description="Дата создания рецензии")


class ReviewUUIDMixin(BaseModel):
    id: UUID = Field(..., description="Идентификатор рецензии")
    film_id: UUID = Field(..., description="Идентификатор фильма")
    user_id: UUID = Field(..., description="Автор рецензии")


class ReviewDetailResponse(TimestampMixin, TextFieldMixin, ReviewUUIDMixin):
    user_score: int | None = Field(..., description="Оценка пользователя привязанная к фильму")
    like_count: int = Field(..., description="Количесвто лайков рецензии")
    dislike_count: int = Field(..., description="Количество дизлайков рецензии")


class ReviewModifiedResponse(TimestampMixin, TextFieldMixin, ReviewUUIDMixin):
    """Модель ответа добавления/изменения рецензии"""


class ReviewModifiedRequest(TextFieldMixin):
    """Модель запроса добавления/изменения рецензии"""


class ReviewRateResponse(TimestampMixin):
    review_id: UUID = Field(..., description="Идентификатор рецензии")
    user_id: UUID = Field(..., description="Автор лайка")
    is_like: bool = Field(..., description="Тип оценки рецензии (True = лайк, False = Дизлайк)")
