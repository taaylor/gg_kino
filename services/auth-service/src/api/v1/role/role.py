from http import HTTPStatus
from typing import Annotated

from api.v1.role.schemas import BodyRoleDetail, Role, RoleDetail
from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse
from services.role import RoleService, get_role_service

router = APIRouter()


@router.get(path="/", response_model=list[Role], description="Список ролей сервиса")
async def get_roles(service: Annotated[RoleService, Depends(get_role_service)]) -> list[Role]:
    roles = await service.get_roles()
    return roles


@router.get(
    path="/{role_code}",
    response_model=RoleDetail | None,
    description="Детальная информация роли сервиса",
)
async def get_role(
    service: Annotated[RoleService, Depends(get_role_service)],
    role_code: Annotated[str, Path(description="Идентификатор роли")],
) -> RoleDetail | None:
    role = await service.get_role(pk=role_code)
    return role


@router.post(
    path="/",
    response_model=RoleDetail,
    status_code=HTTPStatus.CREATED,
    description="Добавление новой роли в сервис",
)
async def create_role(
    service: Annotated[RoleService, Depends(get_role_service)],
    request_body: Annotated[RoleDetail, Body(description="Тело запроса")],
) -> RoleDetail | dict[str, str]:

    role = await service.create_role(request_body=request_body)
    return role


@router.put(path="/{role_code}", description="Обновление роли сервиса", response_model=RoleDetail)
async def update_role(
    service: Annotated[RoleService, Depends(get_role_service)],
    request_body: Annotated[BodyRoleDetail, Body(description="Тело запроса")],
    role_code: Annotated[str, Path(description="Идентификатор роли")],
) -> RoleDetail:

    role = await service.update_role(pk=role_code, request_body=request_body)

    return role


@router.delete(
    path="/{role_code}",
    description="Удаление роли в сервисе",
)
async def destroy_role(
    service: Annotated[RoleService, Depends(get_role_service)],
    role_code: Annotated[str, Path(description="Идентификатор роли")],
) -> JSONResponse:
    await service.destroy_role(pk=role_code)
    return JSONResponse(
        status_code=HTTPStatus.OK, content={"message": f"роль успешно удалена {role_code=}"}
    )
