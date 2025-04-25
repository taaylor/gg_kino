from http import HTTPStatus
from typing import Annotated

from api.v1.role.schemas import BodyRoleDetail, Role, RoleDetail
from fastapi import APIRouter, Body, Depends, Path
from services.role import RoleService, get_role_service

router = APIRouter()


@router.get(path="/", response_model=list[Role], description="Список ролей сервиса")
async def get_roles(service: Annotated[RoleService, Depends(get_role_service)]) -> list[Role]:
    roles = await service.get_roles()
    return roles


@router.get(
    path="/{role_code}", response_model=RoleDetail | None, description="Детальная информация о роли"
)
async def get_role(
    service: Annotated[RoleService, Depends(get_role_service)],
    role_code: Annotated[str, Path(description="Идентификатор роли")],
) -> RoleDetail | None:
    role = await service.get_role(pk=role_code)
    return role


@router.post(
    path="/", response_model=RoleDetail, status_code=HTTPStatus.CREATED, description="Создание роли"
)
async def create_role(
    service: Annotated[RoleService, Depends(get_role_service)],
    request_body: Annotated[RoleDetail, Body(description="Тело запроса")],
) -> RoleDetail | dict[str, str]:

    role = await service.create_role(request_body=request_body)
    return role


@router.put(path="/{role_code}", description="Обновление роли", response_model=RoleDetail)
async def update_role(
    service: Annotated[RoleService, Depends(get_role_service)],
    request_body: Annotated[BodyRoleDetail, Body(description="Тело запроса")],
    role_code: Annotated[str, Path(description="Идентификатор роли")],
) -> RoleDetail:

    role = await service.update_role(pk=role_code, request_body=request_body)

    return role
