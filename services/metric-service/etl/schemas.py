from uuid import UUID

from pydantic import BaseModel, Field


class MessageModel(BaseModel):
    user_session: UUID | None = Field(
        None,
        description="session_id",
    )
    user_uuid: UUID | None = Field(
        None,
        description="user_id",
    )
    ip_address: str | None = Field(
        None,
        description="IP пользователя",
    )
    user_agent: str = Field(
        ...,
        description="IP пользователя",
    )
    film_uuid: UUID | None = Field(
        None,
        description="UUID фильма",
    )
    event_type: str = Field(
        ...,
        description="Тип события",
    )
    message_event: str = Field(
        ...,
        description="Описание события",
    )
    event_params: dict[str, str] = Field(
        default_factory=dict,
        description="Параметры события",
    )
    event_timestamp: str = Field(
        ...,
        description="Время события",
    )
    user_timestamp: str = Field(
        ...,
        description="Время события в часовом поясе клиента",
    )
