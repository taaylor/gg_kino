from datetime import datetime
from uuid import UUID

from models.enums import NotificationMethod, Priority
from pydantic import BaseModel


class UserProfile(BaseModel):
    user_id: UUID
    username: str
    first_name: str
    last_name: str
    gender: str
    role: str
    email: str
    is_fictional_email: bool
    is_email_notify_allowed: bool
    is_verified_email: bool
    user_timezone: str
    created_at: datetime


class Film(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float | None
    description: str | None
    genre: list[dict]
    actors: list[dict]
    writers: list[dict]
    directors: list[dict]
    type: str


class LikeNotification(BaseModel):
    id: UUID
    user_id: UUID
    source: str
    target_sent_at: datetime
    added_queue_at: datetime
    event_type: str
    updated_at: datetime
    method: NotificationMethod
    priority: Priority
    event_data: dict
    created_at: datetime
