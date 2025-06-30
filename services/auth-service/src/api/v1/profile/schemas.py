from datetime import datetime
from uuid import UUID

from models.models_types import GenderEnum
from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    user_id: UUID = Field(..., description="Уникальный идентификатор пользователя в системе")
    username: str = Field(..., description="Логин пользователя")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str = Field(..., description="Фамилия пользователя")
    gender: GenderEnum = Field(..., description="Пол: male/female")
    role: str = Field(..., description="Код уровня доступа")
    email: str = Field(..., description="Основной email адрес пользователя")
    is_fictional_email: bool = Field(..., description="Признак временного/технического email")
    is_notification_email: bool = Field(
        ..., description="Разрешение на отправку уведомлений на этот email"
    )
    is_verification_email: bool = Field(
        ..., description="Подтверждён ли email (верификация пройдена)"
    )
    user_timezone: str = Field(
        ..., description="Часовой пояс пользователя в формате 'Europe/Moscow'"
    )
    date_create_account: datetime = Field(
        ..., description="Дата и время регистрации аккаунта в UTC"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "gender": "MALE",
                "role": "user",
                "email": "john.doe@example.com",
                "is_fictional_email": False,
                "is_notification_email": True,
                "is_verification_email": True,
                "user_timezone": "America/New_York",
                "date_create_account": "2023-01-15T14:30:00Z",
            }
        }
