from auth_utils import Permissions
from pydantic import BaseModel, Field


class Permission(BaseModel):
    """Модель представления права доступа в системе"""

    permission: Permissions = Field(
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
        example=[
            {
                "permission": "FREE_FILMS",
                "descriptions": "Возможность просматривать бесплатные фильмы",
            }
        ],
    )


class RoleDetailResponse(RoleDetailRequest):
    """Базовая модель ответа для создания роли через API"""

    pass


class RoleResponse(BaseModel):
    """Упрощенное представление роли (для списков и краткой информации)"""

    role: str = Field(..., description="Системное название роли", example="content_moderator")
    descriptions: str | None = Field(
        description="Краткое описание назначения роли", example="Роль для модерации контента"
    )


class RoleDetailUpdateRequest(BaseModel):
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


class MessageResponse(BaseModel):
    message: str = Field(..., description="Сообщение состояния HTTP")
