from api.v1.schemes_base import UserProfileBase
from pydantic import UUID4, BaseModel, Field


class ProfileInternalRequest(BaseModel):
    user_ids: list[UUID4] = Field(
        description="Идентификаторы пользователей, для которых необходимо получить профиль",
        min_length=1,
        max_length=100,
    )


class ProfileInternalResponse(UserProfileBase):
    """Профиль пользователя"""


class ProfilePaginateInternalResponse(BaseModel):
    """Профиль пользователя"""

    profiles: list[UserProfileBase] = Field(
        description="Список профилей пользователей",
    )
    page_current: int = Field(
        description="Номер текущей страницы",
        ge=1,
    )
    page_size: int = Field(
        description="Общее количество пользователей",
        ge=1,
    )
    page_total: int = Field(
        description="Общее количество страниц",
        ge=1,
    )
