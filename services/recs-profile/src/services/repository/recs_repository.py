from uuid import UUID

from core.config import app_config
from models.models import UserRecs
from services.repository.base_repository import BaseRepository
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.decorators import sqlalchemy_universal_decorator


class RecsRepository(BaseRepository[UserRecs]):
    """Репозиторий для работы с экземплярами npl в базе данных."""

    @sqlalchemy_universal_decorator
    async def add_now_rec(self, session: AsyncSession, rec: UserRecs) -> UserRecs:
        # Получаем все существующие рекомендации
        stmt = (
            select(UserRecs.id)
            .where(UserRecs.user_id == rec.user_id)
            .order_by(UserRecs.created_at.desc())
            .offset(app_config.count_rec_for_user - 1)
            .with_for_update(skip_locked=True)
        )
        result = await session.execute(stmt)

        ids_to_delete = result.scalars().all()
        if ids_to_delete:
            del_stmt = delete(UserRecs).where(UserRecs.id.in_(ids_to_delete))
            await session.execute(del_stmt)

        session.add(rec)
        await session.flush()
        return rec

    @sqlalchemy_universal_decorator
    async def fetch_recs_from_db(
        self, session: AsyncSession, user_ids: list[UUID]
    ) -> list[UserRecs]:
        stmt = select(self.model).where(UserRecs.user_id.in_(user_ids))
        result = await session.execute(stmt)
        return list(result.scalars().all())


def get_recs_repository() -> RecsRepository:
    """Возвращает экземпляр репозитория для работы с npl."""
    return RecsRepository(UserRecs)
