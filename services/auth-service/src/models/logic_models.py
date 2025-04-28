from uuid import UUID

from pydantic import BaseModel, Field


class SessionUserData(BaseModel):
    user_id: UUID
    session_id: UUID | None = Field(None)
    username: str
    user_agent: str | None
    role_code: str
    permissions: list[str]
