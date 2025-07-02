from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class GenderEnum(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class UserProfile(BaseModel):
    user_id: UUID
    username: str
    first_name: str
    last_name: str
    gender: GenderEnum
    role: str
    email: str
    is_fictional_email: bool
    is_email_notify_allowed: bool
    is_verified_email: bool
    user_timezone: str
    created_at: datetime
