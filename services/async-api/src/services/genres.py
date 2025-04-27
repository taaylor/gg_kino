import json
import logging
from functools import lru_cache
from uuid import UUID

from api.v1.genre.schemas import GenreResponse
from core.config import app_config
from db.cache import Cache, get_cache
from db.database import BaseDB
from db.elastic import get_repository
from fastapi import Depends
from models.schemas_logic import GenreLogic
from utils.decorators import elastic_handler_exeptions

logger = logging.getLogger(__name__)

CACHE_ALL_GENRES_KEY = "genres:all"
CACHE_CURRENT_GENRE_KEY = "genres:current:"
CACHE_GENRES_CACHE_EXPIRES = app_config.cache_expire_in_seconds


class GenreRepository:
    """Реализует работу с постоянным хранилищем данных для сервиса Жанров"""

    GENRES_INDEX = "genres"

    def __init__(self, repository: BaseDB):
        self.repository = repository

    @elastic_handler_exeptions
    async def get_from_db_by_id(self, genre_id: UUID) -> GenreLogic | None:
        """Получает один жанр из ElasticSearch по id"""
        logger.debug(f"Получаю жанр id:{genre_id} из ElasticSearch")
        es_response = await self.repository.get_object_by_id(
            index=self.GENRES_INDEX, object_id=genre_id
        )
        if not es_response:
            logger.error(f"В результате запроса жанра id:{genre_id} жанр не был найден в ES.")
            return None

        genre = GenreLogic.model_validate(es_response)
        logger.info(f"В результате запроса жанра id:{genre_id} из ES получен {genre}.")

        return genre

    @elastic_handler_exeptions
    async def get_from_db_list(self) -> list[GenreLogic]:
        """Получает все жанры из ElasticSearch"""
        logger.debug("Получаю все жанры из ElasticSearch")
        query = {"query": {"match_all": {}}}
        es_response = await self.repository.get_list(index=self.GENRES_INDEX, body=query, size=1000)

        if not es_response:
            logger.error("В результате запроса всех жанров в ES ничего не нашлось.")
            return []

        genres = [GenreLogic.model_validate(genre) for genre in es_response]
        logger.info(f"В результате запроса всех жанров из ES получен список жанров {genres}.")

        return genres


class GenreService:
    """Реализует бизнес логику получения жанров"""

    def __init__(self, cache: Cache, repository: GenreRepository) -> None:
        self.cache = cache
        self.repository = repository

    async def _get_cached_data(self, key: str) -> str | None:
        """Получает данные из кэша по ключу"""
        logger.debug(f"Запрашиваю данные из кэша с ключом: {key}.")
        return await self.cache.get(key=key)

    async def _set_cache_data(self, key: str, value: str, expire: int) -> None:
        """Сохраняет данные в кэш"""
        logger.debug(f"Сохраняю данные в кэш с ключом: {key}.")
        await self.cache.background_set(key=key, value=value, expire=expire)

    async def get_genres_list(self) -> list[GenreResponse]:
        """Получает список всех жанров."""

        cached_genres = await self._get_cached_data(CACHE_ALL_GENRES_KEY)

        if cached_genres:
            genres = [GenreResponse(**genre) for genre in json.loads(cached_genres)]
            logger.info(f"Список жанров получен из кэша, всего жанров {len(genres)}.")
            return genres

        logger.debug("В кэше нет жанров, запрашиваю в БД.")
        db_genres = await self.repository.get_from_db_list()

        if not db_genres:
            logger.error("Список жанров из БД пуст.")
            return []

        genres = [GenreResponse(uuid=genre.id, name=genre.name) for genre in db_genres]

        cache_value = json.dumps([genre.model_dump(mode="json") for genre in genres])
        await self._set_cache_data(
            key=CACHE_ALL_GENRES_KEY, value=cache_value, expire=CACHE_GENRES_CACHE_EXPIRES
        )

        logger.info(
            f"""Список жанров будет сохранён в кэш с ключом
            {CACHE_ALL_GENRES_KEY}, всего жанров {len(genres)}."""
        )
        return genres

    async def get_genre_by_id(self, genre_id: UUID) -> GenreResponse | None:
        """Получает один жанр по ID"""
        cache_key = CACHE_CURRENT_GENRE_KEY + str(genre_id)
        cached_genre = await self._get_cached_data(cache_key)

        if cached_genre:
            genre = GenreResponse(**json.loads(cached_genre))
            logger.info(f"Жанр получен из кэша: {genre}.")
            return genre

        logger.debug(f"В кэше нет жанра {genre_id=}, запрашиваю в БД.")
        db_genre = await self.repository.get_from_db_by_id(genre_id=genre_id)
        if not db_genre:
            logger.warning(f"Жанр {genre_id=} не найден в БД.")
            return None

        genre = GenreResponse(uuid=db_genre.id, name=db_genre.name)

        cache_value = genre.model_dump_json()
        await self._set_cache_data(
            key=cache_key, value=cache_value, expire=CACHE_GENRES_CACHE_EXPIRES
        )

        logger.info(f"Жанр с {genre_id=} будет сохранён в кэш с: {cache_key=}.")
        return genre


@lru_cache
def get_genre_service(
    cache: Cache = Depends(get_cache), repository: BaseDB = Depends(get_repository)
) -> GenreService:

    genre_repository = GenreRepository(repository=repository)
    return GenreService(cache=cache, repository=genre_repository)
