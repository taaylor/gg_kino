from uuid import UUID

from models.models_types import GenderEnum
from pydantic import BaseModel, Field


class ChangeUsernameRequest(BaseModel):
    username: str = Field(..., min_length=4, max_length=50)


class ChangePasswordRequest(BaseModel):
    password: str = Field(...)
    repeat_password: str = Field(...)


class AssignRoleRequest(BaseModel):
    role: str = Field(...)


class UserResponse(BaseModel):
    user_id: UUID = Field(...)
    username: str = Field(..., min_length=4, max_length=30)
    first_name: str | None = Field(None, min_length=4, max_length=30)
    last_name: str | None = Field(None, min_length=4, max_length=30)
    gender: GenderEnum | None = Field(None)
    email: str = Field(...)


class UserCredResponse(BaseModel):
    user_id: UUID = Field(...)
    email: str = Field(...)


class UserRoleResponse(UserResponse):
    role: str = Field(...)


class MessageResponse(BaseModel):
    message: str = Field(..., description="Сообщение состояния HTTP")
