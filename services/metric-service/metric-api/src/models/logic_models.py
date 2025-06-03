from datetime import datetime
from typing import Dict
from uuid import UUID

from pydantic import BaseModel, Field


class EntryEvent(BaseModel):
    """Входящее событие от клиента"""

    film_uuid: UUID | None = Field(None, description="Идентификатор фильма")
    event_type: str = Field(description="Тип события")
    message_event: str | None = Field(None, description="Сообщение события")
    user_timestamp: datetime | None = Field(None, description="Время события на клиенте")
    event_params: Dict[str, str] = Field(
        default_factory=dict, description="Дополнительные параметры события"
    )


class MetricEvent(BaseModel):
    """Логическая модель события метрики"""

    id: str = Field(description="Уникальный идентификатор события")
    user_session: str | None = Field(None, description="Идентификатор сессии пользователя")
    user_uuid: str | None = Field(
        None, description="Уникальный идентификатор пользователя в формате UUID"
    )
    ip_address: str | None = Field(None, description="IP адрес пользователя")
    film_uuid: str | None = Field(None, description="Идентификатор фильма")
    event_type: str = Field(description="Тип события")
    user_agent: str | None = Field(None, description="Клиентское устройство пользователя")
    message_event: str | None = Field(None, description="Сообщение события")
    event_timestamp: datetime = Field(description="Время события на сервере")
    user_timestamp: datetime | None = Field(None, description="Время события на клиенте")
    event_params: Dict[str, str] = Field(
        default_factory=dict, description="Дополнительные параметры события"
    )
