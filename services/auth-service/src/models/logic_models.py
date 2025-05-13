from uuid import UUID

from pydantic import BaseModel, Field

from .models_types import GenderEnum


class SessionUserData(BaseModel):
    user_id: UUID
    session_id: UUID | None = Field(None)
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
