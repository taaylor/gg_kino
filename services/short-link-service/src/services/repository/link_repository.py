import logging
from functools import lru_cache

from models.models import ShortLink
from services.repository.base_repository import BaseRepository
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.decorators import sqlalchemy_universal_decorator

logger = logging.getLogger(__name__)


class LinkRepository(BaseRepository[ShortLink]):

    @sqlalchemy_universal_decorator
    async def check_path(self, session: AsyncSession, path: str) -> bool:
        stmt = select(exists().where(ShortLink.short_path == path))
        # Получится зарос типа: SELECT(EXISTS(SELECT ... FROM short_link WHERE short_path='path'))
        return bool(await session.scalar(stmt))

    @sqlalchemy_universal_decorator
    async def fetch_original_by_short(self, session: AsyncSession, path: str) -> ShortLink | None:
        stmt = (
            select(ShortLink)
            .where(ShortLink.short_path == path, ShortLink.is_archive.is_(False))
            .with_for_update(skip_locked=True)
        )
        result = await session.execute(stmt)
        link = result.scalars().first()
        if link:
            link.uses_count += 1
        return link


@lru_cache
def get_link_repository() -> LinkRepository:
    return LinkRepository()
