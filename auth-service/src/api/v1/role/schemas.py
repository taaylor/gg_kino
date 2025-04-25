from models.models_types import PermissonEnum
from pydantic import BaseModel, Field


class Permission(BaseModel):
    permission: PermissonEnum = Field(...)
    descriptions: str | None = Field(description="Описание права доступа")


class RoleDetail(BaseModel):
    role: str = Field(..., description="Наименование роли")
    descriptions: str | None = Field(description="Описание роли")
    permissions: list[Permission] = Field(description="Список прав доступа")


class Role(BaseModel):
    role: str = Field(..., description="Наименование роли")
    descriptions: str | None = Field(description="Описание роли")


class BodyRoleDetail(BaseModel):
    descriptions: str | None = Field(description="Описание роли")
    permissions: list[Permission] = Field(description="Список прав доступа")
