from uuid import UUID

from pydantic import BaseModel


class ChangeUsernameRequest(BaseModel):
    id: UUID
    username: str


class ChangePasswordRequest(BaseModel):
    id: UUID
    password: str
    repeat_password: str


class AssignRoleRequest(BaseModel):
    role: str
