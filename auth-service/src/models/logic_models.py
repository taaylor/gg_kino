from uuid import UUID

from pydantic import BaseModel


class SessionUserDataData(BaseModel):
    user_id: UUID
    user_agent: str | None
    role_code: str
    permissions: list[str] | None
