from uuid import UUID

from models.models_types import GenderEnum
from pydantic import BaseModel


class SessionUserData(BaseModel):
    user_id: UUID
    session_id: UUID | None = None
    username: str
    user_agent: str | None
    role_code: str
    permissions: list[str]


class OAuthUserInfo(BaseModel):
    social_id: str
    social_name: str
    first_name: str | None
    last_name: str | None
    gender: GenderEnum | None


class RegisteredNotifyContext(BaseModel):
    confirmation_link: str


class RegisteredNotify(BaseModel):
    user_id: UUID
    event_type: str = "USER_REGISTERED"
    source: str = "AUTH-SERVICE"
    method: str = "EMAIL"
    priority: str = "HIGH"
    event_data: RegisteredNotifyContext
