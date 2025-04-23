from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class Gender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class AccessTokenField(BaseModel):
    access_token: str = Field(...)


class RefreshTokenField(BaseModel):
    refresh_token: str = Field(...)


class Session(RefreshTokenField, AccessTokenField):
    expires_at: datetime = Field(...)


class UserFields(BaseModel):
    username: str = Field(..., min_length=4, max_length=30)
    email: str = Field(...)
    first_name: str | None = Field(None, min_length=4, max_length=30)
    last_name: str | None = Field(None, min_length=4, max_length=30)
    gender: Gender = Field(...)


class RegisterRequest(UserFields):
    password: str = Field(...)


class RegisterResponce(UserFields):
    user_id: UUID = Field(...)
    session: Session = Field(...)


class LoginRequest(BaseModel):
    email: str = Field(...)
    password: str = Field(...)


class LoginResponce(Session):
    access_token: str = Field(...)
    refresh_token: str = Field(...)
    expires_at: datetime = Field(...)


class RefreshRequest(RefreshTokenField):
    refresh_token: str = Field(...)


class RefreshResponce(Session):
    access_token: str = Field(...)
    refresh_token: str = Field(...)
    expires_at: datetime = Field(...)
