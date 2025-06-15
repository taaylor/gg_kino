import json
import logging
from functools import lru_cache
from uuid import UUID

from api.v1.rating.schemas import AvgRatingResponse, ScoreResponse
from core.config import app_config
from db.cache import Cache, get_cache
from fastapi import Depends
from services.rating_repository import RatingRepository, get_rating_repository

logger = logging.getLogger(__name__)

CACHE_KEY_AVG_RATING = "films:avg_rating:"


class RatingService:
    """Сервис для работы с рейтингом фильмов."""

    def __init__(
        self,
        cache: Cache,
        repository: RatingRepository,
    ):
        """
        Инициализирует сервис с кешем и репозиторием.

        :param cache: Экземпляр Cache для кеширования результатов.
        :param repository: Репозиторий RatingRepository для работы с БД.
        """
        self.cache = cache
        self.repository = repository

    async def get_average_rating(self, film_id: UUID) -> AvgRatingResponse | None:
        """
        Возвращает рейтинг фильма

        :param film_id: UUID фильма, для которого нужно получить средний рейтинг.
        :return: Экземпляр AvgRatingResponse с полями:
                 - film_id: UUID фильма
                 - avg_rating: среднее арифметическое оценок (float)
                 - count_votes: количество голосов (int);
                 или None, если для фильма нет оценок.
        """
        cache_key = CACHE_KEY_AVG_RATING + str(film_id)
        avg_rating = await self.cache.get(cache_key)

        if avg_rating:
            logger.debug(f"Рейтинг фильма {str(film_id)} получен из кеша по ключу: {cache_key}")
            return AvgRatingResponse.model_validate(json.loads(avg_rating))

        avg_rating = await self.repository.calculate_average_rating(
            self.repository.collection.film_id == film_id
        )

        if not avg_rating:
            return None
        result = avg_rating[0]
        await self.cache.background_set(
            key=cache_key, value=result.model_dump_json(), expire=app_config.cache_expire_in_seconds
        )
        logger.debug(f"Рейтинг фильма {str(film_id)} будет сохранён в кеш по ключу {cache_key}.")
        return AvgRatingResponse(**result.model_dump())

    async def set_user_score(self, user_id: UUID, film_id: UUID, score: int) -> ScoreResponse:
        """
        Сохраняет/обновляет оценку фильма поставленную авторизованным пользователем.

        :param user_id: UUID пользователя, ставящего оценку.
        :param film_id: UUID фильма, для которого ставится оценка.
        :param score: Оценка пользователя (int, строго 1–10).
        :return: Экземпляр ScoreResponse с полями:
                 - user_id: UUID пользователя
                 - film_id: UUID фильма
                 - created_at: время создания/вставки документа
                 - updated_at: время последнего обновления
                 - score: значение оценки
        """

        cache_key = CACHE_KEY_AVG_RATING + str(film_id)
        document = await self.repository.upsert(
            self.repository.collection.user_id == user_id,
            self.repository.collection.film_id == film_id,
            user_id=user_id,
            film_id=film_id,
            score=score,
        )
        result = ScoreResponse(
            user_id=document.user_id,
            film_id=document.film_id,
            created_at=document.created_at,
            updated_at=document.updated_at,
            score=document.score,
        )
        logger.debug(
            f"Пользователь - {str(user_id)}\n,"
            f" оценил фильм {str(film_id)}\n."
            f" Оценка: {score}."
        )
        avg_rating = await self.repository.calculate_average_rating(
            self.repository.collection.film_id == film_id
        )
        await self.cache.background_set(
            key=cache_key,
            value=avg_rating[0].model_dump_json(),
            expire=app_config.cache_expire_in_seconds,
        )
        logger.debug(f"Рейтинг фильма {str(film_id)} будет сохранён в кеш по ключу {cache_key}.")
        return result

    async def delete_user_score(self, user_id: UUID, film_id: UUID) -> None:
        """
        Удаляет оценку фильма поставленную авторизованным пользователем.

        :param user_id: UUID пользователя.
        :param film_id: UUID фильма.
        :return: None.
        """

        cache_key = CACHE_KEY_AVG_RATING + str(film_id)
        await self.repository.delete_document(
            self.repository.collection.user_id == user_id,
            self.repository.collection.film_id == film_id,
        )
        logger.debug(
            f"Пользователь - {str(user_id)}\n," f" отозвал оценку фильма {str(film_id)}\n."
        )
        # if <документ> найден (True), то кешируем, если нет (False), то нет:
        avg_rating = await self.repository.calculate_average_rating(
            self.repository.collection.film_id == film_id
        )
        await self.cache.background_set(
            key=cache_key,
            value=avg_rating[0].model_dump_json(),
            expire=app_config.cache_expire_in_seconds,
        )
        logger.debug(f"Рейтинг фильма {str(film_id)} будет сохранён в кеш по ключу {cache_key}.")


@lru_cache()
def get_rating_service(
    cache: Cache = Depends(get_cache),
    repository: RatingRepository = Depends(get_rating_repository),
) -> RatingService:
    return RatingService(cache, repository)
