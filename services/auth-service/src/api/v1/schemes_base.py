from datetime import datetime
from uuid import UUID

from models.models_types import GenderEnum
from pydantic import BaseModel, Field


class UserProfileBase(BaseModel):
    user_id: UUID = Field(..., description="Уникальный идентификатор пользователя в системе")
    username: str = Field(..., description="Логин пользователя")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str = Field(..., description="Фамилия пользователя")
    gender: GenderEnum = Field(..., description="Пол: male/female")
    role: str = Field(..., description="Код уровня доступа")
    email: str = Field(..., description="Основной email адрес пользователя")
    is_fictional_email: bool = Field(..., description="Признак временного/технического email")
    is_email_notify_allowed: bool = Field(
        ..., description="Разрешение на отправку уведомлений на этот email"
    )
    is_verified_email: bool = Field(..., description="Подтверждён ли email (верификация пройдена)")
    user_timezone: str = Field(
        ..., description="Часовой пояс пользователя в формате 'Europe/Moscow'"
    )
    created_at: datetime = Field(..., description="Дата и время регистрации аккаунта в UTC")
