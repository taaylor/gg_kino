from typing import Annotated
from uuid import UUID

from api.v1.genre.schemas import GenreResponse
from fastapi import APIRouter, Depends, Path
from services.genres import GenreService, get_genre_service

router = APIRouter()


@router.get(
    path="/",
    response_model=list[GenreResponse],
    response_model_exclude_none=True,
    summary="Список жанров",
    description=(
        "Возвращает список всех доступных жанров. "
        "Используется для отображения фильтрации по жанрам или общей информации в интерфейсе."
    ),
)
async def get_genres_list(
    genre_service: Annotated[GenreService, Depends(get_genre_service)],
) -> list[GenreResponse]:
    genre_list = await genre_service.get_genres_list()
    return genre_list


@router.get(
    path="/{genre_id}",
    response_model=GenreResponse | None,
    response_model_exclude_none=True,
    summary="Информация о жанре",
    description=(
        "Возвращает информацию о жанре по его уникальному идентификатору (UUID). "
        "Используется для отображения информации при фильтрации или просмотре \
            детальной информации о жанре."
    ),
)
async def get_genre_by_id(
    genre_id: Annotated[UUID, Path(title="Уникальный идентификатор жанра")],
    genre_service: Annotated[GenreService, Depends(get_genre_service)],
) -> GenreResponse | None:
    genre = await genre_service.get_genre_by_id(genre_id=genre_id)
    return genre
