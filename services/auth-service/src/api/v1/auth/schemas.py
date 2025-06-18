from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class Gender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class AccessTokenField(BaseModel):
    access_token: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Токен доступа для авторизации",
    )


class RefreshTokenField(BaseModel):
    refresh_token: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Токен для обновления сессии",
    )


class Session(RefreshTokenField, AccessTokenField):
    expires_at: datetime = Field(..., description="Дата и время истечения токена")


class UserFields(BaseModel):
    username: str = Field(
        ...,
        min_length=4,
        max_length=30,
        description="Юзернейм пользователя",
    )
    email: str = Field(
        ...,
        min_length=5,
        max_length=254,
        description="Электронная почта пользователя",
    )
    first_name: str | None = Field(
        None,
        min_length=4,
        max_length=30,
        description="Имя пользователя (опционально)",
    )
    last_name: str | None = Field(
        None,
        min_length=4,
        max_length=30,
        description="Фамилия пользователя (опционально)",
    )
    gender: Gender = Field(..., description="Пол пользователя")


class RegisterRequest(UserFields):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Пароль для регистрации",
    )


class RegisterResponse(UserFields):
    user_id: UUID = Field(..., description="Уникальный идентификатор пользователя")
    session: Session = Field(..., description="Сессия пользователя")


class LoginRequest(BaseModel):
    email: str = Field(
        ...,
        min_length=5,
        max_length=254,
        description="Электронная почта пользователя",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Пароль пользователя",
    )


class LoginResponse(Session):
    access_token: str = Field(..., description="Токен доступа для авторизации")
    refresh_token: str = Field(..., description="Токен для обновления сессии")
    expires_at: datetime = Field(..., description="Дата и время истечения токена")


class RefreshResponse(Session):
    pass


class EntryPoint(BaseModel):
    user_agent: str = Field(..., description="Точка входа в аккаунт")
    created_at: datetime = Field(..., description="Время входа в аккаунт")


class SessionsHistory(BaseModel):
    actual_user_agent: str = Field(..., description="Актуальная точка входа в аккаунт")
    create_at: datetime = Field(..., description="Время входа в аккаунт")
    history: list[EntryPoint] = Field(
        default=[],
        description="Последние дествия в аккаунте",
    )


class MessageResponse(BaseModel):
    message: str = Field(..., description="Сообщение состояния HTTP")


class OAuthParams(BaseModel):
    client_id: str = Field(
        description="Идентификатор клиента, выданный сервисом для вашего приложения.",
    )
    scope: str = Field(description="Список запрашиваемых разрешений")
    state: str = Field(description="Уникальная строка. Подписывается сервером.")
    response_type: str = Field(description="Тип ответа от OAuth-провайдера")
    authorize_url: str = Field(description="URL эндпоинта авторизации")


class OAuthProviderParams(BaseModel):
    url_auth: str = Field(
        description="URL для перенаправления пользователя на страницу авторизации провайдера.",
    )
    params: OAuthParams = Field(
        description="Параметры авторизации, используемые для формирования URL \
             и передачи фронтенду.",
    )


class OAuthSocialResponse(BaseModel):
    yandex: OAuthProviderParams = Field(
        description="Объект, содержащий параметры и URL для авторизации через Yandex.",
    )
