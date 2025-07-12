from models.enums import Priority
from pydantic import BaseModel, ConfigDict, Field


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
    template_id: str | None = Field(description="id шаблона")

    model_config = ConfigDict(extra="ignore")


class UpdateStatusSchema(BaseModel):
    """Схема для хранения статусов отправленных событий."""

    sent_success: list[str] = Field(
        default_factory=list, description="Список успешно отправленных уведомлений"
    )
    failure: list[str] = Field(
        default_factory=list, description="Список уведомлений, которые не удалось отправить"
    )
