import logging
from functools import lru_cache
from uuid import UUID

from api.v1.bookmark.schemas import (
    ChangeBookmarkResponse,
    CreateBookmarkRequest,
    CreateBookmarkResponse,
    FetchBookmarkList,
)
from db.cache import Cache, get_cache
from fastapi.exceptions import HTTPException
from models.logic_models import FilmBookmarkState
from models.models import Bookmark
from services.bookmark_repository import BookmarkRepository, get_bookmark_repository

logger = logging.getLogger(__name__)


class BookmarkService:
    """Класс реализую бизнес логику работы с списком просмотра фильмов"""

    __slots__ = ("cache", "repository")

    def __init__(self, cache, repository) -> None:
        self.cache: Cache = cache
        self.repository: BookmarkRepository = repository

    async def add_bookmark_by_film_id(
        self, user_id: UUID, film_id: UUID, request_body: CreateBookmarkRequest
    ) -> CreateBookmarkResponse:

        logger.info(f"Пользователь: {user_id=} добавляет фильм: {film_id=} в закладки")

        # new_user_bookmark = Bookmark(
        #     user_id=user_id,
        #     film_id=film_id,
        #     comment=request_body.comment,
        #     status=FilmBookmarkState.NOTWATCHED,
        # )

        await self.repository.upsert(
            self.repository.collection.user_id == user_id,
            self.repository.collection.film_id == film_id,
            user_id=user_id,
            film_id=film_id,
            comment=request_body.comment,
            status=FilmBookmarkState.NOTWATCHED,
        )

        inserted_bookmark = await self.repository.get_document(
            self.repository.collection.user_id == user_id,
            self.repository.collection.film_id == film_id,
        )
        if inserted_bookmark:
            return CreateBookmarkResponse(
                film_id=inserted_bookmark.film_id,
                comment=inserted_bookmark.comment,
                created_at=inserted_bookmark.created_at,
                updated_at=inserted_bookmark.updated_at,
            )

        raise HTTPException(status_code=400, detail="Фильм не найден")

    async def remove_bookmark_by_film_id(self):
        pass

    async def fetch_watchlist_by_user_id(self) -> FetchBookmarkList:
        pass

    async def update_bookmark_status_by_film_id(self) -> ChangeBookmarkResponse:
        pass

    async def validate_film_id(self) -> bool:
        pass


@lru_cache()
def get_bookmark_service() -> BookmarkService:
    cache = get_cache()
    repository = get_bookmark_repository()
    return BookmarkService(cache, repository)
