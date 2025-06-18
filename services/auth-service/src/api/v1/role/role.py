import logging
from http import HTTPStatus
from typing import Annotated

from api.v1.role.schemas import (
    MessageResponse,
    RoleDetailRequest,
    RoleDetailResponse,
    RoleDetailUpdateRequest,
    RoleResponse,
)
from auth_utils import LibAuthJWT, Permissions, access_permissions_check, auth_dep
from fastapi import APIRouter, Body, Depends, Path
from rate_limite_utils import rate_limit
from services.role_service import RoleService, get_role_service

logger = logging.getLogger(__name__)

router = APIRouter()

REQUIRED_PERMISSIONS = {Permissions.CRUD_ROLE.value}


@router.get(
    path="/",
    response_model=list[RoleResponse],
    summary=f"Список всех ролей (REST-стиль). Необходимые разрешения:{REQUIRED_PERMISSIONS}",
    description="Получение списка всех пользовательских ролей киносервиса",
    response_description="Успешное получение списка ролей в формате массива объектов",
)
@rate_limit()
@access_permissions_check(REQUIRED_PERMISSIONS)
async def get_roles(
    service: Annotated[RoleService, Depends(get_role_service)],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> list[RoleResponse]:
    roles = await service.get_roles()
    return roles


@router.get(
    path="/{role_code}",
    response_model=RoleDetailResponse | None,
    summary=f"Детали роли (REST-стиль). Необходимые разрешения:{REQUIRED_PERMISSIONS}",
    description="Получение детальной информации о конкретной роли киносервиса",
    response_description="Объект с полными данными роли или null если роль не найдена",
)
@rate_limit()
@access_permissions_check(REQUIRED_PERMISSIONS)
async def get_role(
    service: Annotated[RoleService, Depends(get_role_service)],
    role_code: Annotated[str, Path(description="Уникальный идентификатор роли (код)")],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> RoleDetailResponse | None:
    role = await service.get_role(pk=role_code)
    return role


@router.post(
    path="/",
    response_model=RoleDetailResponse,
    status_code=HTTPStatus.CREATED,
    summary=f"Создать роль (REST-стиль). Необходимые разрешения:{REQUIRED_PERMISSIONS}",
    description="Создание новой роли в системе киносервиса",
    response_description="Объект созданной роли с полными данными и присвоенным идентификатором",
)
@access_permissions_check(REQUIRED_PERMISSIONS)
async def create_role(
    service: Annotated[RoleService, Depends(get_role_service)],
    request_body: Annotated[
        RoleDetailRequest,
        Body(description="Данные для создания роли в формате JSON"),
    ],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> RoleDetailResponse | dict[str, str]:
    role = await service.create_role(request_body=request_body)
    return role


@router.put(
    path="/{role_code}",
    summary=f"Обновить роль (REST-стиль). Необходимые разрешения:{REQUIRED_PERMISSIONS}",
    description="Обновление данных существующей роли киносервиса",
    response_model=RoleDetailResponse,
    response_description="Объект с обновленными данными роли",
)
@rate_limit()
@access_permissions_check(REQUIRED_PERMISSIONS)
async def update_role(
    service: Annotated[RoleService, Depends(get_role_service)],
    request_body: Annotated[
        RoleDetailUpdateRequest,
        Body(description="Обновленные данные роли в формате JSON"),
    ],
    role_code: Annotated[
        str,
        Path(description="Уникальный идентификатор обновляемой роли"),
    ],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> RoleDetailResponse:
    role = await service.update_role(pk=role_code, request_body=request_body)
    return role


@router.delete(
    path="/{role_code}",
    summary=f"Удалить роль (REST-стиль). Необходимые разрешения:{REQUIRED_PERMISSIONS}",
    description="Удаление роли из системы киносервиса",
    response_description="Статус операции удаления с сообщением о результате",
    response_model=MessageResponse,
)
@access_permissions_check(REQUIRED_PERMISSIONS)
async def destroy_role(
    service: Annotated[RoleService, Depends(get_role_service)],
    role_code: Annotated[
        str,
        Path(description="Уникальный идентификатор удаляемой роли"),
    ],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> MessageResponse:
    await service.destroy_role(pk=role_code)
    return MessageResponse(message=f"Роль успешно удалена {role_code=}")
