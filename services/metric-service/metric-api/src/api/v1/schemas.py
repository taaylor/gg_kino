from apiflask import Schema
from marshmallow import fields


class EventRequest(Schema):
    """Схема для входящих запросов с событиями"""

    film_uuid = fields.UUID(allow_none=True, metadata={"description": "Идентификатор фильма"})
    event_type = fields.String(required=True, metadata={"description": "Тип события"})
    message_event = fields.String(allow_none=True, metadata={"description": "Сообщение события"})
    user_timestamp = fields.DateTime(allow_none=True, metadata={"description": "Время события"})
    event_params = fields.Dict(
        keys=fields.String(),
        values=fields.String(),
        metadata={"description": "Дополнительные параметры события"},
    )


class EventResponse(Schema):
    """Схема для ответов API"""

    id = fields.UUID(metadata={"description": "Уникальный идентификатор события"})
    status = fields.String(metadata={"description": "Статус обработки события"})
    timestamp = fields.DateTime(metadata={"description": "Время создания события"})
