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
    object_id: UUID | None = Field(
        None, description="Уникальный идентификатор объекта с которым произошло действие"
    )
    method: NotificationMethod = Field(..., description="Канал для уведомления пользователя")
    priority: Priority = Field(
        Priority.LOW,
        description="Приоритет, с которым будет отправлено уведомление. HIGH доставляются без учёта таймзоны пользователя",  # noqa: E501
    )
    event_data: dict | None = Field(
        ..., description="Контекст события, которое привело к запросу на нотификацию"
    )
    target_sent_at: datetime | None = Field(
        datetime.now(timezone.utc), description="Желаемое время отправки уведомления"
    )


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
