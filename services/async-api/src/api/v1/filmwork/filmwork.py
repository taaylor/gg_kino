from typing import Annotated
from uuid import UUID

from api.v1.filmwork.schemas import (
    FilmDetailResponse,
    FilmListResponse,
    FilmSorted,
    SearchByVectorRequest,
)
from auth_utils import LibAuthJWT, Permissions, auth_dep
from core.config import app_config
from fastapi import APIRouter, Body, Depends, Path, Query
from services.filmwork import FilmService, get_film_service

router = APIRouter()

DEFAULT_PERMISSION = Permissions.FREE_FILMS.value


@router.get(
    "/search",
    response_model=list[FilmListResponse],
    summary="Поиск кинопроизведений по ключевым словам",
    description=(
        "Полнотекстовый поиск кинопроизведений по ключевым словам. "
        "Поиск осуществляется по названию, описанию, именам актеров, режиссеров и сценаристов. "
        "Поддерживает сортировку и пагинацию."
    ),
    response_description="Список кинопроизведений с UUID, названием и рейтингом",
)
async def film_search(
    film_service: Annotated[FilmService, Depends(get_film_service)],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    query: Annotated[
        str,
        Query(description="Поле запроса по поиску кинопроизведений"),
    ] = "",
    page_size: Annotated[
        int,
        Query(ge=1, le=100, description="Количество записей на странице"),
    ] = 50,
    page_number: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
) -> list[FilmListResponse]:
    """Endpoint для поискового запроса по кинопроизведениям"""
    await authorize.jwt_optional()
    user_permissions = {DEFAULT_PERMISSION}
    user_token = await authorize.get_raw_jwt()
    if user_token:
        user_permissions = set(user_token.get("permissions"))

    if not query:
        return []

    total_pages = await film_service.get_total_pages(page_size, user_permissions)

    if page_number > total_pages:
        return []

    search_films = await film_service.get_list_film_by_search_query(
        query=query,
        page_size=page_size,
        page_number=page_number,
        user_permissions=user_permissions,
    )

    return search_films


@router.get(
    "/{film_id}",
    response_model=FilmDetailResponse | None,
    summary="Получить подробную информацию о кинопроизведении",
    description=(
        "Возвращает полную информацию о кинопроизведении по его уникальному "
        "идентификатору (UUID). "
        "В ответ включены название, рейтинг, описание, жанры, актерский состав, \
        сценаристы и режиссеры."
    ),
    response_description="Подробная информация о кинопроизведении",
)
async def film_detail(
    film_service: Annotated[FilmService, Depends(get_film_service)],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    film_id: Annotated[UUID, Path(description="UUID кинопроизведения")],
) -> FilmDetailResponse | None:
    """Endpoint для получения детальной информации о кинопроизведении по UUID"""
    await authorize.jwt_optional()
    user_permissions = {DEFAULT_PERMISSION}
    user_token = await authorize.get_raw_jwt()
    if user_token:
        user_permissions = set(user_token.get("permissions"))

    film = await film_service.get_film_by_id(
        film_id=film_id,
        user_permissions=user_permissions,
    )

    return film


@router.get(
    "/",
    response_model=list[FilmListResponse],
    summary="Получить список кинопроизведений с фильтрацией и сортировкой",
    description=(
        "Возвращает список кинопроизведений с возможностью сортировки по рейтингу \
            и фильтрации по жанрам. "
        "Поддерживает пагинацию. Можно указать один или несколько жанров."
    ),
    response_description="Список кинопроизведений с UUID, названием и рейтингом",
)
async def film_list(
    film_service: Annotated[FilmService, Depends(get_film_service)],
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    sort: Annotated[
        FilmSorted,
        Query(description="Сортировка по рейтингу кинопроизведения"),
    ] = FilmSorted.RATING_DESC,
    genre: Annotated[
        list[UUID],
        Query(
            description="Фильтр по жанрам, принимает один жанр или список жанров (UUID)",
        ),
    ] = None,
    page_size: Annotated[
        int,
        Query(ge=1, le=100, description="Количество записей на странице"),
    ] = 50,
    page_number: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
) -> list[FilmListResponse]:
    """Endpoint для получения кинопроизведений с использованием фильтрации"""
    await authorize.jwt_optional()
    user_permissions = {DEFAULT_PERMISSION}
    user_token = await authorize.get_raw_jwt()
    if user_token:
        user_permissions = set(user_token.get("permissions"))
    total_pages = await film_service.get_total_pages(
        page_size=page_size,
        user_permissions=user_permissions,
    )

    if page_number > total_pages:
        return []

    films = await film_service.get_list_film(
        sort=sort,
        genre=genre,
        page_size=page_size,
        page_number=page_number,
        user_permissions=user_permissions,
    )

    return films


@router.post(
    path="/search-by-vector",
    summary="Поиск фильмов по семантическому вектору",
    description=(
        "Принимает на вход JSON с эмбеддингом"
        f" (список из {app_config.embedding_dims} float-значений),"
        " полученным от NL-сервиса, и возвращает страницу фильмов, упорядоченных "
        " по косинусному сходству этого вектора к эмбеддингам фильмов."
    ),
    response_description=(
        "Список фильмов в формате FilmListResponse," " отсортированный по релевантности"
    ),
    response_model=list[FilmListResponse],
)
async def search_by_vector(
    film_service: Annotated[FilmService, Depends(get_film_service)],
    request_body: Annotated[
        SearchByVectorRequest,
        Body(
            description=(
                f"JSON с одним эмбеддинг‑вектором (список из {app_config.embedding_dims} float)"
            )
        ),
    ],
    page_size: Annotated[
        int,
        Query(ge=1, le=100, description="Количество записей на странице"),
    ] = 50,
    page_number: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
) -> list[FilmListResponse]:
    """
    Endpoint для поискового запроса по семантическому эмбеддингу для кинопроизведений.
    """
    films = await film_service.get_films_by_vector(
        vector=request_body.vector,
        page_size=page_size,
        page_number=page_number,
    )
    return films
