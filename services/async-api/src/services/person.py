import json
import logging
from functools import lru_cache
from typing import Any
from uuid import UUID

from api.v1.filmwork.schemas import FilmListResponse
from api.v1.person.schemas import PersonInFilmsResponse, PersonResponse
from core.config import app_config
from db.cache import Cache, get_cache
from db.database import BaseDB
from db.elastic import get_repository
from fastapi import Depends
from models.schemas_logic import PersonLogic

logger = logging.getLogger(__name__)

CACHE_KEY_PERSONS = "persons"
CACHE_FILMS_CACHE_EXPIRES = app_config.cache_expire_in_seconds


class PersonRepository:
    PERSONS_INDEX = "persons"
    MOVIES_INDEX = "movies"

    def __init__(self, repository: BaseDB):
        self.repository = repository

    async def get_person_by_id(self, person_id: UUID) -> PersonResponse | None:
        """Получает информацию о персоне по ее идентификатору.

        :param person_id: Идентификатор персоны.
        :return: Объект `PersonResponse` с информацией о персоне и ее фильмах или None,
        если персона не найдена.
        """
        person = await self.repository.get_object_by_id(
            index=self.PERSONS_INDEX,
            object_id=person_id,
        )

        if not person:
            return None
        body = self.get_query_films_by_person(person_id=person_id)
        films_sources = await self.repository.get_list(self.MOVIES_INDEX, body)
        films = self.convert_roles_and_films_to_model_response(
            person_id=person_id,
            films_sources=films_sources,
        )
        person_result = PersonResponse(
            uuid=person_id,
            full_name=person["name"],
            films=films,
        )
        return person_result

    def convert_roles_and_films_to_model_response(
        self,
        person_id: UUID,
        films_sources: list[dict],
    ) -> list[PersonInFilmsResponse]:
        """Извлекает роли персоны из списка фильмов.

        :param person_id: Идентификатор персоны.
        :param films_sources: Список фильмов с информацией о ролях.
        :return: Список объектов PersonInFilmsResponse с ролями персоны.
        """
        film_roles = []
        if not films_sources:
            return film_roles

        for film in films_sources:
            roles = list(
                self.collects_roles(
                    film,
                    person_id,
                ),
            )
            film_roles.append(
                PersonInFilmsResponse(
                    uuid=film["id"],
                    roles=roles,
                ),
            )
        return film_roles

    async def get_person_by_id_films(
        self,
        person_id: UUID,
    ) -> list[FilmListResponse] | list:
        """Получает информацию о персоне по ее идентификатору.

        :param person_id: Идентификатор персоны.
        :return: Объект `PersonResponse` с информацией о персоне и ее фильмах или None,
        если персона не найдена.
        """
        person_data = await self.repository.get_object_by_id(
            index=self.PERSONS_INDEX,
            object_id=person_id,
        )
        if person_data is None:
            return []
        person = PersonLogic.model_validate(person_data)
        body = self.get_query_films_by_person(person_id=person.id)
        films_sources = await self.repository.get_list(
            self.MOVIES_INDEX,
            body,
            size=1000,
        )

        # ! конвертируем фильмы в модель Response
        films = self.convert_films_to_model_response(films_sources=films_sources)
        return films

    def convert_films_to_model_response(
        self,
        films_sources: list[dict],
    ) -> list[FilmListResponse]:
        """Извлекает роли персоны в фильмах.

        :param person_id: ID персоны.
        :param films_sources: Список фильмов.
        :return: Список объектов PersonInFilmsResponse.
        """
        films = [
            FilmListResponse(
                uuid=film.get("id"),
                title=film.get("title"),
                imdb_rating=film.get("imdb_rating"),
                type=film.get("type"),
            )
            for film in films_sources
        ]
        return films

    def get_query_films_by_person(self, person_id: str) -> dict[str, Any]:
        """Выполняет запрос в Elasticsearch для получения фильмов, в которых участвовал человек.

        :param person_id: Идентификатор персоны.
        :return: Результат поиска в Elasticsearch.
        """
        return {
            "query": {
                "bool": {
                    "should": [
                        self.build_nested_query_detail("actors", person_id),
                        self.build_nested_query_detail("directors", person_id),
                        self.build_nested_query_detail("writers", person_id),
                    ],
                    "minimum_should_match": 1,
                },
            },
        }

    def collects_roles(self, film_source: dict, person_id: str) -> list[str]:
        """Извлекает роли, которые выполнял человек в фильме.

        :param film_source:
            Словарь с данными о фильме, содержащий списки актеров, режиссеров и сценаристов.
        :param person_id: Уникальный идентификатор персоны.
        :return:
            Множество ролей (например, {"actor", "director", "writer"}),
            если персона участвовала в фильме.
        """
        roles = []
        roles.extend(
            {"actor" for p in film_source["actors"] if p["id"] == str(person_id)},
        )
        roles.extend(
            {"director" for p in film_source["directors"] if p["id"] == str(person_id)},
        )
        roles.extend(
            {"writer" for p in film_source["writers"] if p["id"] == str(person_id)},
        )
        return roles

    def build_nested_query_detail(self, field: str, person_id: UUID) -> dict:
        """Формирует вложенный запрос для поиска персоны по заданному полю в Elasticsearch.

        :param field:
            Поле, в котором выполняется поиск
            (например, "actors", "directors" или "writers").
        :param person_id: Уникальный идентификатор персоны.
        :return: Словарь с запросом для Elasticsearch, выполняющий поиск по заданному полю.
        """
        return {
            "nested": {"path": field, "query": {"term": {f"{field}.id": person_id}}},
        }

    def get_person_ids(self, persons: list[str]) -> dict[str, str]:
        """Извлекает идентификаторы и имена персон из результатов поиска Elasticsearch.

        :param persons: Список документов из индекса "persons".
        :return: Словарь, где ключ — ID персоны, значение — её имя.
        """
        person_ids = {}
        for hit in persons:
            p_id = hit.get("id")
            p_name = hit.get("name")
            person_ids[p_id] = p_name
        return person_ids

    def convert_many_person_to_model_response(
        self,
        person_ids: dict[str, str],
        many_roles: dict[str, Any],
    ) -> list[PersonResponse]:
        """Формирует список персон с их ролями и фильмами на основе данных из Elasticsearch.

        :param person_ids: Словарь ID и имён персон.
        :param many_roles: Данные о фильмах, в которых участвуют персоны.
        :return: Список объектов PersonResponse с информацией о фильмах и ролях.
        """
        result = []
        for p_id in person_ids:
            list_roles = []
            if many_roles:
                for film in many_roles:
                    roles = self.collects_roles(film, p_id)
                    if roles:
                        list_roles.append(
                            PersonInFilmsResponse(
                                uuid=film["id"],
                                roles=roles,
                            ),
                        )
                result.append(
                    PersonResponse(
                        uuid=p_id,
                        full_name=person_ids[p_id],
                        films=list_roles,
                    ),
                )
            result.append(
                PersonResponse(uuid=p_id, full_name=person_ids[p_id], films=[]),
            )
        return result

    async def get_person_by_search(
        self,
        query,
        page_number,
        page_size,
    ) -> list[PersonResponse]:
        """Выполняет поиск персон по имени с пагинацией и возвращает их данные вместе с фильмами.

        :param query: Поисковый запрос (имя персоны).
        :param page_number: Номер страницы результатов.
        :param page_size: Количество записей на странице.
        :return: Список персон с их ролями и фильмами.
        """
        body = self.query_person_by_search(query)

        persons = await self.repository.get_list(
            index=self.PERSONS_INDEX,
            body=body,
            page_number=page_number,
            page_size=page_size,
        )
        if not persons:
            return []

        person_ids = self.get_person_ids(persons)
        body = self.get_query_many_roles(list(person_ids))
        films = await self.repository.get_list(index=self.MOVIES_INDEX, body=body)
        persons = self.convert_many_person_to_model_response(person_ids, films)

        return persons

    def build_nested_query_many(self, field: str, person_ids: list[str]) -> dict:
        """Формирует множественный nested-запрос для поиска фильмов, связанных с персонами.

        :param field: Поле ("actors", "writers" или "directors").
        :param person_ids: Список идентификаторов персон.
        :return: Elasticsearch nested-запрос.
        """
        return {
            "nested": {"path": field, "query": {"terms": {f"{field}.id": person_ids}}},
        }

    def get_query_many_roles(
        self,
        person_ids: list[str],
    ) -> dict[str, Any]:
        """Выполняет запрос в Elasticsearch для получения фильмов,
        в которых участвовали много персон.

        :param person_ids: Список идентификаторов персон.
        :return: Документ с результатами поиска фильмов.
        """
        return {
            "query": {
                "bool": {
                    "should": [
                        self.build_nested_query_many("actors", person_ids),
                        self.build_nested_query_many("writers", person_ids),
                        self.build_nested_query_many("directors", person_ids),
                    ],
                    "minimum_should_match": 1,
                },
            },
            "size": 10000,  # Максимальное количество фильмов, можно уменьшить
        }

    def query_person_by_search(self, query: str) -> dict[str, Any]:
        """Выполняет запрос к Elasticsearch для поиска персон по имени с учётом пагинации.

        :param query: Поисковый запрос (имя персоны).
        :param from_value: Смещение результатов (начальная позиция).
        :param page_size: Количество записей на странице.
        :return: Документ с результатами поиска персон.
        """
        return {
            "query": {"match": {"name": {"query": query, "fuzziness": "auto"}}},
        }


class PersonService:
    def __init__(
        self,
        cache: Cache,
        repository: PersonRepository,
    ) -> None:
        self.cache = cache
        self.repository = repository

    async def get_person_by_id(self, person_id: UUID) -> PersonResponse | None:
        """Получает информацию о персоне по ее идентификатору.

        :param person_id: Идентификатор персоны.
        :return: Объект `PersonResponse` с информацией о персоне и ее фильмах или None,
        если персона не найдена.
        """
        redis_key = f"{CACHE_KEY_PERSONS}:{person_id}"
        data = await self.cache.get(redis_key)
        if data:
            logger.debug(f"Person {person_id} в кеше. Возвращаяю кеш.")
            return PersonResponse.model_validate_json(data)
        logger.debug(f"Person {person_id} отсутствует в кеше. Запрашиваю из БД.")
        person_result = await self.repository.get_person_by_id(person_id=person_id)

        if not person_result:
            return None

        await self.cache.background_set(
            redis_key,
            person_result.model_dump_json(),
            CACHE_FILMS_CACHE_EXPIRES,
        )
        logger.debug(f"Person {person_id} будет сохранён в кеш по ключу {redis_key}.")
        return person_result

    async def get_person_by_id_films(
        self,
        person_id: UUID,
    ) -> list[FilmListResponse] | list:
        """Получает информацию о персоне по ее идентификатору.

        :param person_id: Идентификатор персоны.
        :return: Объект `PersonResponse` с информацией о персоне и ее фильмах или None,
        если персона не найдена.
        """
        redis_key = f"{CACHE_KEY_PERSONS}:{person_id}:films"
        data = await self.cache.get(redis_key)
        if data:
            logger.debug(f"Список фильмов Person {person_id} в кеше. Возвращаю кеш.")
            return [FilmListResponse.model_validate(film) for film in json.loads(data)]
        logger.debug(
            f"Список фильмов Person {person_id} отсутствует в кеш. Запрашиваю из БД.",
        )
        films = await self.repository.get_person_by_id_films(person_id)
        if not films:
            return []
        data_json = json.dumps([film.model_dump(mode="json") for film in films])
        await self.cache.background_set(
            redis_key,
            data_json,
            expire=CACHE_FILMS_CACHE_EXPIRES,
        )
        logger.debug(
            f"Список фильмов Person {person_id} будет сохранён в кеш по ключу {redis_key}.",
        )
        return films

    async def get_person_by_search(
        self,
        query,
        page_number,
        page_size,
    ) -> list[PersonResponse]:
        """Выполняет поиск персон по имени с пагинацией и возвращает их данные вместе с фильмами.

        :param query: Поисковый запрос (имя персоны).
        :param page_number: Номер страницы результатов.
        :param page_size: Количество записей на странице.
        :return: Список персон с их ролями и фильмами.
        """
        redis_key = f"{CACHE_KEY_PERSONS}:{query}:{page_number}:{page_size}"
        data = await self.cache.get(redis_key)
        if data:
            logger.debug(f"Список Person по запросу {query} в кеше. Возвращаю кеш.")
            return [
                PersonResponse.model_validate(person) for person in json.loads(data)
            ]
        logger.debug(
            f"Список Person по запросу {query} отсутствует в кеше. Запрашиваю из БД.",
        )
        persons = await self.repository.get_person_by_search(
            query,
            page_number,
            page_size,
        )
        if not persons:
            return []
        data_json = json.dumps([person.model_dump(mode="json") for person in persons])
        await self.cache.background_set(
            redis_key,
            data_json,
            expire=CACHE_FILMS_CACHE_EXPIRES,
        )
        logger.debug(
            f"Список Person по запросу {query} будет сохранён в кеш по ключу {redis_key}.",
        )
        return persons


@lru_cache
def get_person_service(
    cache: Cache = Depends(get_cache),
    repository: BaseDB = Depends(get_repository),
) -> PersonService:
    person_repository = PersonRepository(repository=repository)
    return PersonService(cache, person_repository)
