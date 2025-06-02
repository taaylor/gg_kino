from apiflask import Schema
from marshmallow import fields


class EventRequest(Schema):
    """Схема для входящих запросов с событиями"""

    film_uuid = fields.UUID(allow_none=True, metadata={"description": "Идентификатор фильма"})
    event_type = fields.String(
        required=True, metadata={"description": "Тип события", "example": "like"}
    )
    message_event = fields.String(
        allow_none=True,
        metadata={
            "description": "Сообщение события",
            "example": "Пользователь поставил лайк фильму",
        },
    )
    user_timestamp = fields.DateTime(
        allow_none=True,
        metadata={
            "description": "Время события в таймзоне пользователя",
            "example": "2025-06-02T17:30:00+03:00",
        },
    )
    event_params = fields.Dict(
        keys=fields.String(),
        values=fields.String(),
        metadata={
            "description": "Дополнительные параметры события",
            "example": {"rating": "5", "watch_position": "00:45:30"},
        },
    )
