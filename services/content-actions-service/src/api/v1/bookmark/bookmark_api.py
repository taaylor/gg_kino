import logging
from typing import Annotated
from uuid import UUID

from api.v1.bookmark.schemas import (
    ChangeBookmarkRequest,
    ChangeBookmarkResponse,
    CreateBookmarkRequest,
    CreateBookmarkResponse,
    FetchBookmarkList,
)
from auth_utils import LibAuthJWT, auth_dep
from fastapi import APIRouter, Body, Depends, Path, Query, status
from rate_limite_utils import rate_limit
from services.bookmark_service import BookmarkService, get_bookmark_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    path="/{film_id}",
    response_model=CreateBookmarkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить фильм в закладки",
    description="Сохраняет фильм в список просмотра со статусом: 'Не просмотрен'",
)
@rate_limit()
async def create_bookmark(
    service: Annotated[BookmarkService, Depends(get_bookmark_service)],
    request_body: Annotated[CreateBookmarkRequest, Body()],
    film_id: Annotated[UUID, Path(description="Уникальный идентификатор фильма")],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> CreateBookmarkResponse:
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    user_id = UUID(decrypted_token.get("user_id"))  # type: ignore

    result = await service.add_bookmark_by_film_id(
        user_id=user_id, film_id=film_id, request_body=request_body
    )

    return result


@router.delete(
    path="/{film_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаляет фильм из закладок",
    description="Удаляет фильм из списка сохранённых в список для просмотра",
)
@rate_limit()
async def delete_bookmark(
    service: Annotated[BookmarkService, Depends(get_bookmark_service)],
    film_id: Annotated[UUID, Path(description="Уникальный идентификатор фильма")],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> None:
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    user_id = UUID(decrypted_token.get("user_id"))  # type: ignore

    await service.remove_bookmark_by_film_id(user_id=user_id, film_id=film_id)


@router.get(
    path="/watchlist",
    response_model=FetchBookmarkList,
    summary="Возвращает список для просмотра пользователя",
    description="""
        Возвращает список для просмотра пользователя, по умолчанию для user_id из
        JWT токена авторизации, но можно указать user_id другого пользователя""",
)
@rate_limit()
async def fetch_watchlist(
    service: Annotated[BookmarkService, Depends(get_bookmark_service)],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    other_user_id: Annotated[
        UUID | None,
        Query(
            description="user_id пользователя, для которого необходимо получить список для просмотра. По умолчанию получает из JWT токена.",  # noqa: E501
        ),
    ] = None,
    page_size: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Количество закладок на одной странице",
        ),
    ] = 50,
    skip_page: Annotated[
        int,
        Query(
            ge=0,
            le=100,
            description="Количество страниц для пропуска",
        ),
    ] = 0,
) -> FetchBookmarkList:
    await authorize.jwt_required()

    if other_user_id:
        user_id = other_user_id
    else:
        decrypted_token = await authorize.get_raw_jwt()
        user_id = UUID(decrypted_token.get("user_id"))  # type: ignore

    result = await service.fetch_watchlist_by_user_id(
        user_id=user_id, page_size=page_size, skip_page=skip_page
    )

    return result


@router.post(
    path="/watch-status/{film_id}",
    response_model=ChangeBookmarkResponse,
    summary="Изменяет статус просмотра фильма и/или комментарий",
    description="Проставляет на фильме статус просмотра WATCHED/NOTWATCHED и/или комментарий",
)
@rate_limit()
async def change_watch_status(
    service: Annotated[BookmarkService, Depends(get_bookmark_service)],
    request_body: Annotated[ChangeBookmarkRequest, Body()],
    film_id: Annotated[UUID, Path(description="Уникальный идентификатор фильма")],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> ChangeBookmarkResponse:
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    user_id = UUID(decrypted_token.get("user_id"))  # type: ignore

    result = await service.update_bookmark_by_film_id(
        user_id=user_id, film_id=film_id, request_body=request_body
    )

    return result
