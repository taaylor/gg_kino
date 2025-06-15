import logging
from typing import Annotated
from uuid import UUID

from api.v1.bookmark.schemas import (
    ChangeBookmarkResponse,
    CreateBookmarkRequest,
    CreateBookmarkResponse,
    FetchBookmarkList,
    FilmBookmarkState,
)
from auth_utils import LibAuthJWT, Permissions, access_permissions_check, auth_dep
from fastapi import APIRouter, Body, Depends, Path, Query
from rate_limite_utils import rate_limit

logger = logging.getLogger(__name__)

router = APIRouter()

# API Методы:
# 1. Добавить фильм в закладки +
# 2. Удалить фильм из закладок +
# 3. Получить список фильмов в закладках +
# 4. Получить список фильмов в закладках у другого пользователя +
# 5. Пометить филь просмотренным +


@router.post(
    path="/{film_id}",
    response_model=CreateBookmarkResponse,
    summary="Добавить фильм в закладки",
    description="Сохраняет фильм в список просмотра со статусом: 'Не просмотрен'",
)
# @rate_limit()
async def create_bookmark(
    service: None,
    request_body: Annotated[CreateBookmarkRequest, Body()],
    film_id: Annotated[UUID, Path(description="Уникальный идентификатор фильма")],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> CreateBookmarkResponse:
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    user_id = UUID(decrypted_token.get("user_id"))  # type: ignore

    return None


@router.delete(
    path="/{film_id}",
    status_code=204,
    summary="Удаляет фильм из закладок",
    description="Удаляет фильм из списка сохранённых в список для просмотра",
)
# @rate_limit()
async def delete_bookmark(
    service: None,
    film_id: Annotated[UUID, Path(description="Уникальный идентификатор фильма")],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> None:
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    user_id = UUID(decrypted_token.get("user_id"))  # type: ignore

    return None


@router.get(
    path="/watchlist",
    response_model=FetchBookmarkList,
    summary="Возвращает список для просмотра для пользователя",
    description="Удаляет фильм из списка сохранённых в список для просмотра",
)
# @rate_limit()
async def fetch_watchlist(
    service: None,
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    user_id: Annotated[
        UUID | None,
        Query(
            description="user_id пользователя, для которого необходимо получить список для просмотра. По умолчанию получает из JWT токена.", # noqa E501
        ),
    ] = None,
) -> FetchBookmarkList:
    await authorize.jwt_required()
    decrypted_token = await authorize.get_raw_jwt()
    user_id = UUID(decrypted_token.get("user_id"))  # type: ignore

    return None


@router.post(
    path="/watch-status/{film_id}",
    response_model=ChangeBookmarkResponse,
    summary="Изменяет статус просмотра фильма",
    description="Проставляет на фильме статус просмотра WATCHED/NOTWATCHED",
)
async def change_watch_status(
    service: None,
    film_id: Annotated[UUID, Path(description="Уникальный идентификатор фильма")],
    watch_status: Annotated[FilmBookmarkState, Query(description="статус просмотра фильма")],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
) -> ChangeBookmarkResponse:

    return None
