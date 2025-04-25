from typing import Annotated
from uuid import UUID

from api.v1.filmwork.schemas import FilmListResponse
from api.v1.person.schemas import PersonResponse
from fastapi import APIRouter, Depends, Query
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get(
    "/search",
    response_model=list[PersonResponse] | list,
    summary="Поиск персон",
    description="Полнотекстовый поиск персон по имени. Поддерживает пагинацию результатов.",
    response_description="Список персон, подходящих под поисковый запрос",
)
async def person_search(
    person_service: Annotated[PersonService, Depends(get_person_service)],
    query: Annotated[
        str,
        Query(
            title="Параметр запроса",
            description="Параметр запроса для полнотекстового поиска персоны по имени",
            min_length=1,
            max_length=100,
        ),
    ],
    page_number: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=100, description="Количество записей на странице")
    ] = 50,
) -> list[PersonResponse] | list:
    persons = await person_service.get_person_by_search(query, page_number, page_size)
    return persons


@router.get(
    "/{person_id}",
    response_model=PersonResponse | None,
    summary="Информация о персоне",
    description="Возвращает детальную информацию о персоне по её уникальному UUID.",
    response_description="UUID, имя и список ролей персоны",
)
async def person_detail(
    person_id: UUID,
    person_service: Annotated[PersonService, Depends(get_person_service)],
) -> PersonResponse | None:
    person = await person_service.get_person_by_id(person_id)
    return person


@router.get(
    "/{person_id}/film",
    response_model=list[FilmListResponse],
    summary="Фильмы с участием персоны",
    description="Возвращает список кинопроизведений, в которых участвовала "
    "персона (актёр, сценарист или режиссёр).",
    response_description="Список кинопроизведений: UUID, название и рейтинг",
)
async def person_detail_films_list(
    person_id: UUID,
    person_service: Annotated[PersonService, Depends(get_person_service)],
) -> list[FilmListResponse]:
    person_films = await person_service.get_person_by_id_films(person_id)
    return person_films
