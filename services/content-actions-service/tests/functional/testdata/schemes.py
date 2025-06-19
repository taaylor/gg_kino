from pydantic import BaseModel, Field
from tests.functional.testdata.model_enum import GenderEnum


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
    gender: GenderEnum = Field(..., description="Пол пользователя")


class RegisterRequest(UserFields):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Пароль для регистрации",
    )


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
