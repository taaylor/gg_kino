from uuid import UUID

from models.enums import Priority
from pydantic import BaseModel, Field


class SingleNotificationRequest(BaseModel):
    user_id: UUID = Field(
        ..., description="Уникальный идентификатор пользователя, которому предназначено уведомление"
    )
    event_type: str = Field(
        ...,
        min_length=5,
        max_length=500,  # noqa: WPS432
        description="Тип уведомления (действие/ситуация, которые привели к отправке уведомления)",
    )
    object_id: UUID | None = Field(
        None, description="Уникальный идентификатор объекта с которым произошло действие"
    )
    priority: Priority = Field(
        Priority.LOW,
        description="Приоритет, с которым будет отправлено уведомление. HIGH доставляются без учёта таймзоны пользователя",  # noqa: E501
    )
    event_context: dict | None = Field(
        ..., description="Контекст события, которое привело к запросу на нотификацию"
    )


class SingleNotificationResponse(BaseModel):
    notification_id: UUID = Field(
        ..., description="Уникальный идентификатор экземпляра уведомления"
    )
