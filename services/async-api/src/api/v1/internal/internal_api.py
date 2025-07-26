from typing import Annotated

from api.v1.filmwork.schemas import FilmListResponse
from api.v1.genre.schemas import GenreResponse
from api.v1.internal.schemas import FilmInternalResponse, FilmsRequest, SearchByVectorRequest
from core.config import app_config
from fastapi import APIRouter, Body, Depends, Query
from services.filmwork import FilmService, get_film_service
from services.genres import GenreService, get_genre_service

router = APIRouter()


@router.post(
    "/fetch-films",
    response_model=list[FilmInternalResponse],
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
    request_body: Annotated[FilmsRequest, Body(description="UUID кинопроизведений")],
) -> list[FilmInternalResponse]:
    """Endpoint для получения детальной информации о кинопроизведениях по UUID"""
    film_ids = request_body.film_ids
    films = await film_service.get_films_by_id_internal(
        film_ids=film_ids,
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


@router.get(
    path="/genres",
    response_model=list[GenreResponse],
    response_model_exclude_none=True,
    summary="Список жанров",
    description=("Возвращает список всех доступных жанров."),
)
async def get_genres_list(
    genre_service: Annotated[GenreService, Depends(get_genre_service)],
) -> list[GenreResponse]:
    genre_list = await genre_service.get_genres_list()
    return genre_list
