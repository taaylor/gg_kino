from uuid import UUID

from pydantic import BaseModel, Field


class MessageModel(BaseModel):
    id: UUID = Field(
        ...,
        description="UUID события",
    )
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


"""
id=str(uuid.uuid4()),
user_session=session_data.get("user_session"),
user_uuid=session_data.get("user_uuid"),
ip_address=session_data.get("ip_address"),
user_agent=session_data.get("user_agent"),
film_uuid=str(getattr(event, "film_uuid", None)),
event_type=getattr(event, "event_type", "other"),
message_event=getattr(event, "message_event", None),
event_params=getattr(event, "event_params", {}),
event_timestamp=datetime.now(timezone.utc),
user_timestamp=getattr(event, "user_timestamp", None),
"""
