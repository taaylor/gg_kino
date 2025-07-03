from typing import Annotated

from api.v1.internal.schemes import ProfileInternalRequest, ProfileInternalResponse
from fastapi import APIRouter, Body, Depends, security
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
        str | None,
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
    return await profile_service.get_users_data_profiles(request_body.user_ids)
