from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class EventRequest(BaseModel):
    film_uuid: UUID | None
    event_type: str
    message_event: str
    user_timestamp: datetime
    event_params: dict[str, Any]
