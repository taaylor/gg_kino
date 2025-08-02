# from datetime import datetime
# from uuid import UUID

# from pydantic import BaseModel, Field

# class Permission(BaseModel):
#     """Модель представления права доступа в системе"""

#     permission: PermissionEnum = Field(
#         ...,
#         description="Тип права доступа из предопределенного перечня",
#         example="FREE_FILMS",
#     )
#     descriptions: str | None = Field(
#         description="Подробное описание назначения и scope права доступа",
#         example="Разрешение на просмотр free фильмов кинотеатра",
#     )


# class RoleDetailRequest(BaseModel):
#     """Базовая модель запроса для создания роли через API"""

#     role: str = Field(..., description="Уникальное название роли", example="UNSUB_USER")
#     descriptions: str | None = Field(
#         description="Подробное описание назначения и привилегий роли",
#         example="Роль для модерации пользовательского контента",
#     )
#     permissions: list[Permission] = Field(
#         ...,
#         description="Список связанных прав доступа",
#         min_items=1,
#         example=[{"permission": "FREE_FILMS", "descriptions": "ЛЯЛЯЛЯ"}],
#     )


# class RoleDetailResponse(RoleDetailRequest):
#     """Базовая модель ответа для создания/получения роли через API"""


# class AccessTokenField(BaseModel):
#     access_token: str = Field(
#         ...,
#         min_length=10,
#         max_length=5000,
#         description="Токен доступа для авторизации",
#     )


# class RefreshTokenField(BaseModel):
#     refresh_token: str = Field(
#         ...,
#         min_length=10,
#         max_length=5000,
#         description="Токен для обновления сессии",
#     )


# class Session(RefreshTokenField, AccessTokenField):
#     expires_at: datetime = Field(..., description="Дата и время истечения токена")


# class UserFields(BaseModel):
#     username: str = Field(
#         ...,
#         min_length=4,
#         max_length=30,
#         description="Юзернейм пользователя",
#     )
#     email: str = Field(
#         ...,
#         min_length=5,
#         max_length=254,
#         description="Электронная почта пользователя",
#     )
#     first_name: str | None = Field(
#         None,
#         min_length=4,
#         max_length=30,
#         description="Имя пользователя (опционально)",
#     )
#     last_name: str | None = Field(
#         None,
#         min_length=4,
#         max_length=30,
#         description="Фамилия пользователя (опционально)",
#     )
#     gender: GenderEnum = Field(..., description="Пол пользователя")


# class RegisterRequest(UserFields):
#     password: str = Field(
#         ...,
#         min_length=8,
#         max_length=128,
#         description="Пароль для регистрации",
#     )


# class RegisterResponse(UserFields):
#     user_id: UUID = Field(..., description="Уникальный идентификатор пользователя")
#     session: Session = Field(..., description="Сессия пользователя")


# class LoginRequest(BaseModel):
#     email: str = Field(
#         ...,
#         min_length=5,
#         max_length=254,
#         description="Электронная почта пользователя",
#     )
#     password: str = Field(
#         ...,
#         min_length=8,
#         max_length=128,
#         description="Пароль пользователя",
#     )


# class RoleResponse(BaseModel):
#     """Упрощенное представление роли (для списков и краткой информации)"""

#     role: str = Field(
#         ...,
#         description="Системное название роли",
#         example="content_moderator",
#     )
#     descriptions: str | None = Field(
#         description="Краткое описание назначения роли",
#         example="Роль для модерации контента",
#     )


# class RoleDetailUpdateRequest(BaseModel):
#     descriptions: str | None = Field(
#         description="Подробное описание назначения и привилегий роли",
#         example="Роль для модерации пользовательского контента",
#     )
#     permissions: list[Permission] = Field(
#         ...,
#         description="Список связанных прав доступа",
#         min_items=1,
#         example=[{"permission": "FREE_FILMS", "descriptions": "ЛЯЛЯЛЯ"}],
#     )
