from pydantic import BaseModel, Field
from tests.functional.testdata.model_enum import GenderEnum, PermissionEnum


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


class UserFields(BaseModel):
    username: str = Field(..., min_length=4, max_length=30, description="Юзернейм пользователя")
    email: str = Field(
        ..., min_length=5, max_length=254, description="Электронная почта пользователя"
    )
    first_name: str | None = Field(
        None, min_length=4, max_length=30, description="Имя пользователя (опционально)"
    )
    last_name: str | None = Field(
        None,
        min_length=4,
        max_length=30,
        description="Фамилия пользователя (опционально)",
    )
    gender: GenderEnum = Field(..., description="Пол пользователя")


class RegisterRequest(UserFields):
    password: str = Field(..., min_length=8, max_length=128, description="Пароль для регистрации")


class LoginRequest(BaseModel):
    email: str = Field(
        ..., min_length=5, max_length=254, description="Электронная почта пользователя"
    )
    password: str = Field(..., min_length=8, max_length=128, description="Пароль пользователя")


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
