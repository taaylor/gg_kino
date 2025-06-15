from functools import lru_cache

from models.models import Bookmark
from services.base_repository import BaseRepository


class BookmarkRepository(BaseRepository[Bookmark]):
    pass


@lru_cache()
def get_bookmark_repository() -> BookmarkRepository:
    return BookmarkRepository(Bookmark)
