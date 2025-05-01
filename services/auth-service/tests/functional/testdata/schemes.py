from pydantic import BaseModel, Field
from tests.functional.testdata.model_enum import PermissionEnum


class Permission(BaseModel):
    """Модель представления права доступа в системе"""

    permission: PermissionEnum = Field(
        ..., description="Тип права доступа из предопределенного перечня", example="FREE_FILMS"
    )
    descriptions: str | None = Field(
        description="Подробное описание назначения и scope права доступа",
        example="Разрешение на просмотр free фильмов кинотеатра",
    )


class RoleDetailRequest(BaseModel):
    """Базовая модель запроса для создания роли через API"""

    role: str = Field(..., description="Уникальное название роли", example="UNSUB_USER")
    descriptions: str | None = Field(
        description="Подробное описание назначения и привилегий роли",
        example="Роль для модерации пользовательского контента",
    )
    permissions: list[Permission] = Field(
        ...,
        description="Список связанных прав доступа",
        min_items=1,
        example=[{"permission": "FREE_FILMS", "descriptions": "ЛЯЛЯЛЯ"}],
    )


class RoleDetailResponse(RoleDetailRequest):
    """Базовая модель ответа для создания/получения роли через API"""

    pass
