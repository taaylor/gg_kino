from typing import Annotated
from uuid import UUID

from api.v1.profile.schemas import ProfileResponse
from auth_utils import LibAuthJWT, auth_dep
from fastapi import APIRouter, Depends, Header, HTTPException, Path, Request, status
from services.profile_service import ProfileService, get_profile_service
from utils.state_manager import validate_apikey_service

router = APIRouter()


@router.get(
    path="/{user_id}",
    description="Возвращает профиль пользователя по id пользователя",
    summary="Получить профиль пользователя",
    response_model=ProfileResponse,
)
async def get_user_profile_info(
    request: Request,
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    user_id: Annotated[UUID, Path(description="Идентификатор пользователя для получения профиля")],
    x_api_key: Annotated[str | None, Header(description="Ключ для доступа к API")] = None,
    x_service_name: Annotated[
        str | None, Header(description="НАименование сервиса, от которого идет запрос")
    ] = None,
) -> ProfileResponse:

    if validate_apikey_service(x_api_key, x_service_name):
        target_user_id = user_id
    else:
        await authorize.jwt_required()
        user_jwt_id = UUID((await authorize.get_raw_jwt()).get("user_id"))

        if user_jwt_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас недостаточно прав для просмотра этого профиля",
            )

        target_user_id = user_jwt_id

    return await profile_service.get_user_data_profile(target_user_id)
