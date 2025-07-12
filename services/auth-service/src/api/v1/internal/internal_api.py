from typing import Annotated

from api.v1.internal.schemes import (
    ProfileInternalRequest,
    ProfileInternalResponse,
    ProfilePaginateInternalResponse,
)
from fastapi import APIRouter, Body, Depends, Query, security
from services.profile_service import ProfileService, get_profile_service
from utils.state_manager import ApiKeyValidate

router = APIRouter()


@router.post(
    path="/fetch-profiles",
    summary="Возвращает в ответе список профилей пользователей",
    description=(
        "Позволяет запросить профили пользователей"
        "передав идентификаторы пользователей в теле запроса "
        "и API ключ в заголовках запроса"
    ),
    response_model=list[ProfileInternalResponse],
)
async def fetch_users_profiles(
    x_api_key: Annotated[
        str,
        Depends(
            security.APIKeyHeader(
                name="X-Api-Key", description="Ключ для достпа к API", auto_error=True
            )
        ),
    ],
    request_body: Annotated[ProfileInternalRequest, Body()],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
) -> list[ProfileInternalResponse]:
    ApiKeyValidate.validate_apikey_service(x_api_key)
    return await profile_service.fetch_users_profiles_list(request_body.user_ids)


@router.post(
    path="/fetch-all-profiles",
    summary="Возвращает в ответе список профилей всех пользователей",
    description=(
        "Позволяет запросить профили всех пользователей"
        "с помощью API ключа в заголовках запроса"
        "с использованием пагинации"
    ),
    response_model=ProfilePaginateInternalResponse,
)
async def fetch_all_users_profiles(
    x_api_key: Annotated[
        str,
        Depends(
            security.APIKeyHeader(
                name="X-Api-Key", description="Ключ для достпа к API", auto_error=True
            )
        ),
    ],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    page_size: Annotated[
        int, Query(ge=1, le=100, description="Количество записей на странице")
    ] = 50,
    page_number: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
) -> ProfilePaginateInternalResponse:
    ApiKeyValidate.validate_apikey_service(x_api_key)
    return await profile_service.fetch_all_users_profiles(
        page_size=page_size, page_number=page_number
    )
