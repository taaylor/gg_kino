import logging
from functools import lru_cache
from uuid import UUID

from core.config import app_config
from db.postgres import get_session_context
from models.enums import RecsSourceType
from models.logic_models import BookMarkEvent, FilmResponse, QueryModel, RatingEvent
from models.models import UserRecs
from services.base_service import BaseService
from services.repository.nlp_repository import RecsRepository, get_recs_repository
from sqlalchemy.ext.asyncio import AsyncSession
from suppliers.embedding_supplier import EmbeddingSupplier, get_embedding_supplier
from suppliers.film_supplier import FilmSupplier, get_film_supplier

logger = logging.getLogger(__name__)


class RecsEventProcessor(BaseService):

    def __init__(
        self,
        repository: RecsRepository,
        session: AsyncSession,
        film_supplier: FilmSupplier,
        embedding_supplier: EmbeddingSupplier,
    ) -> None:
        super().__init__(repository, session)
        self.film_supplier = film_supplier
        self.embedding_supplier = embedding_supplier

    async def event_handler(self, topic: str, message: bytes) -> None:
        event = self._decode_message(topic, message)
        match event:
            case RatingEvent():
                await self._process_rating_event(event)
            case BookMarkEvent():
                await self._process_bookmark_event(event)

    def _decode_message(self, topic: str, message: bytes) -> RatingEvent | BookMarkEvent:
        match topic:
            case app_config.kafka.rec_bookmarks_list_topic:
                decoded_message = message.decode("utf-8")
                logger.info(f"Получено сообщение из топика: {topic}: payload: {decoded_message}")
                return BookMarkEvent.model_validate_json(decoded_message)
            case app_config.kafka.rec_user_ratings_films_topic:
                decoded_message = message.decode("utf-8")
                logger.info(f"Получено сообщение из топика: {topic}: payload: {decoded_message}")
                return RatingEvent.model_validate_json(decoded_message)
            case _:
                logger.error(f"Невозможно обработать событие из топика {topic}")
                raise ValueError(f"Сообщение из неизвестного топика {topic}")

    async def _process_bookmark_event(self, event: BookMarkEvent):
        logger.debug(f"Обрабатываю событие создания закладки: {event.model_dump_json(indent=4)}")

        embedding = await self._fetch_embedding(event.film_id)
        await self._save_rec_to_repository(event, RecsSourceType.ADD_BOOKMARKS, embedding)

    async def _process_rating_event(self, event: RatingEvent):
        logger.debug(f"Обрабатываю событие оценки фильма: {event.model_dump_json(indent=4)}")

        if event.score < app_config.high_rating_score:
            logger.info(
                f"Пользователь недостаточно высоко оценил фильм для создания рекомендации: {event.score}"  # noqa: E501
            )
            return None

        embedding = await self._fetch_embedding(event.film_id)
        await self._save_rec_to_repository(event, RecsSourceType.HIGH_RATING, embedding)

    async def _fetch_embedding(self, film_id: UUID) -> list[float]:
        # TODO: Можно переделать на получение всех фильмов и эмбеддингов пакетом при чтении батча.
        film_description = await self._fetch_film_description(film_id)
        embedding_query = QueryModel(id=film_id, text=film_description)
        embedding = await self.embedding_supplier.fetch_embedding([embedding_query])
        logger.debug(f"Создан эмбеддинг для фильма: {film_id}, {embedding[film_id][:10]}")
        return embedding[film_id]

    async def _fetch_film_description(self, film_id: UUID) -> str:
        films = await self.film_supplier.fetch_films([film_id])
        logger.info(
            f"Для создания рекомендации получен фильм: {films[0].model_dump_json(indent=4)}"
        )
        embedding_text = self._build_embedding_text(films[0])
        logger.debug(f"Для фильма сгенерирован текст будущего эмбеддинга: {embedding_text}")
        return embedding_text

    def _build_embedding_text(
        self,
        film: FilmResponse,
    ) -> str:
        return app_config.template_film_embedding.format(
            title=film.title,
            genres=", ".join([genre.name for genre in film.genre]),
            description=film.description,
            rating_text=film.imdb_rating,
        )

    async def _save_rec_to_repository(
        self,
        event: BookMarkEvent | RatingEvent,
        source_type: RecsSourceType,
        embedding: list[float],
    ):
        rec = UserRecs(
            user_id=event.user_id,
            film_id=event.film_id,
            rec_source_type=source_type,
            embedding=embedding,
        )
        async with self.session as session:
            await self.repository.create_entity(session, rec)


@lru_cache
def create_recs_event_processor() -> RecsEventProcessor:
    session = get_session_context()
    repository = get_recs_repository()
    film_supplier = get_film_supplier()
    embedding_supplier = get_embedding_supplier()

    return RecsEventProcessor(
        repository=repository,
        session=session,
        film_supplier=film_supplier,
        embedding_supplier=embedding_supplier,
    )
