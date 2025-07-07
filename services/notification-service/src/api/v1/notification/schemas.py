from datetime import datetime, timezone
from uuid import UUID

from models.enums import EventType, NotificationMethod, Priority
from pydantic import BaseModel, Field


class SingleNotificationRequest(BaseModel):
    """Запрос на создание одиночного уведомления"""

    user_id: UUID = Field(
        ..., description="Уникальный идентификатор пользователя, которому предназначено уведомление"
    )
    event_type: EventType = Field(
        EventType.TEST,
        description="Тип уведомления (действие/ситуация, которые привели к отправке уведомления)",
    )
    source: str = Field(..., description="Сервис запрашивающий уведомление")
    method: NotificationMethod = Field(..., description="Канал для уведомления пользователя")
    priority: Priority = Field(
        Priority.LOW,
        description="Приоритет, с которым будет отправлено уведомление. HIGH доставляются без учёта таймзоны пользователя",  # noqa: E501
    )
    event_data: dict = Field(
        default_factory=dict,
        description="Контекст события, которое привело к запросу на нотификацию",
    )
    target_sent_at: datetime | None = Field(
        datetime.now(timezone.utc), description="Желаемое время отправки уведомления"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "a88cbbeb-b998-4ca6-aeff-501463dcdaa0",
                    "event_type": "USER_REVIEW_LIKED",
                    "source": "content-api",
                    "method": "WEBSOCKET",
                    "priority": "HIGH",
                    "event_data": {
                        "liked_by_user_id": "cf3d6829-5f95-4e64-acf2-70a6e0f27909",
                        "review_id": "f59ac58a-64a5-41f3-bae4-f4a8aefab8b0",
                        "film_id": "3e5351d6-4e4a-486b-8529-977672177a07",
                    },
                }
            ]
        }
    }


class SingleNotificationResponse(BaseModel):
    """Ответ о создании одиночного уведомления"""

    notification_id: UUID = Field(
        ..., description="Уникальный идентификатор экземпляра уведомления"
    )


class UpdateSendingStatusRequest(BaseModel):
    sent_success: list[UUID] = Field(
        default_factory=list, description="Список успешно отправленных уведомлений"
    )
    failure: list[UUID] = Field(
        default_factory=list, description="Список уведомлений, которые не удалось отправить"
    )


class UpdateSendingStatusResponse(BaseModel):
    updated: list[UUID] = Field(default_factory=list, description="Список обновлённых уведомлений")
