from apiflask import Schema, fields


class EventRequest(Schema):
    user_id = fields.UUID(
        metadata={"description": "Уникальный идентификатор пользователя в формате UUID"}
    )
    user_session = fields.UUID()
    film_uuid = fields.UUID()
    event_type = fields.String()
    message_event = fields.String()
    event_timestamp = fields.DateTime()
    event_params = fields.Dict(keys=fields.String(), values=fields.String())
