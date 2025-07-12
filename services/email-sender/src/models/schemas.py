from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Priority(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


"""
{'id': '58885bed-1eec-4c3a-9f0d-53a18c559c01',
 'user_id': 'c138e471-4ef9-449f-a831-f1932fc4aca6',
 'method': 'EMAIL',
 'source': 'content-api',
 'status': 'PROCESSING',
 'target_sent_at': '2025-07-02T19:08:29.205500Z',
 'actual_sent_at': None,
 'added_queue_at': None,
 'priority': 'LOW',
 'event_type': 'USER_REGISTERED',
 'event_data': {'email': 'user@user.user',
                'gender': 'MALE',
                'username': 'user',
                'last_name': 'user',
                'created_at': False,
                'first_name': 'user',
                'is_verified_email': False,
                'is_fictional_email': False,
                'is_email_notify_allowed': True},
                'user_timezone': 'Europe/Moscow',
                'template_id': None,
                'mass_notification_id': None
                 }
"""


class EventSchemaMessage(BaseModel):
    """Схема сообщения события для очереди."""

    id: str = Field(description="Уникальный идентификатор уведомления")
    user_id: str = Field(description="Идентификатор пользователя, которому адресовано уведомление")
    method: str = Field(
        description="Метод доставки уведомления (например, WEBSOCKET)", exclude=True
    )
    source: str = Field(description="Источник уведомления (например, content-api)", exclude=True)
    status: str = Field(description="Статус уведомления (например, sent, failed)", exclude=True)
    target_sent_at: str = Field(description="Время отправки уведомления пользователю", exclude=True)
    actual_sent_at: str | None = Field(
        default=None, description="Фактическое время отправки уведомления", exclude=True
    )
    added_queue_at: str | None = Field(
        default=None, description="Время добавления уведомления в очередь", exclude=True
    )
    priority: Priority = Field(description="Приоритет уведомления (например, LOW)")
    event_type: str = Field(description="Тип уведомления (например, user_review_liked)")
    event_data: dict = Field(default_factory=dict, description="Данные уведомления")

    model_config = ConfigDict(extra="ignore")


class UpdateStatusSchema(BaseModel):
    """Схема для хранения статусов отправленных событий."""

    sent_success: list[str] = Field(
        default_factory=list, description="Список успешно отправленных уведомлений"
    )
    failure: list[str] = Field(
        default_factory=list, description="Список уведомлений, которые не удалось отправить"
    )
