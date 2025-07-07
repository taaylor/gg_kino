from enum import StrEnum

from pydantic import BaseModel, Field


class Priority(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class NotificationMethod(StrEnum):
    EMAIL = "EMAIL"
    WEBSOCKET = "WEBSOCKET"


class EventSchemaMessage(BaseModel):
    """Схема сообщения события для очереди."""

    id: str = Field(..., description="Уникальный идентификатор события")
    user_id: str = Field(..., description="Идентификатор пользователя, которому адресовано событие")
    source: str = Field(..., description="Источник события (например, content-api)", exclude=True)
    target_sent_at: str = Field(
        ..., description="Время отправки события пользователю", exclude=True
    )
    added_queue_at: str = Field(..., description="Время добавления события в очередь", exclude=True)
    event_type: str = Field(..., description="Тип события (например, user_review_liked)")
    updated_at: str = Field(..., description="Время последнего обновления события", exclude=True)
    method: NotificationMethod = Field(
        ..., description="Метод доставки события (например, WEBSOCKET)", exclude=True
    )
    priority: Priority = Field(..., description="Приоритет события (например, LOW)")
    event_data: dict = Field(..., description="Данные события")
    created_at: str = Field(..., description="Время создания события")


class EventsIdsLogic(BaseModel):
    """Схема для хранения статусов отправленных событий."""

    sent_success: list[str] = Field(
        default_factory=list, description="Список успешно отправленных уведомлений"
    )
    failure: list[str] = Field(
        default_factory=list, description="Список уведомлений, которые не удалось отправить"
    )
