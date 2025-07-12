from db.postgres import Base
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.decorators import sqlalchemy_universal_decorator


class BaseRepository[T: Base]:
    """Базовый репозиторий для работы с хранилищем данных."""

    def __init__(self, model: type[T]) -> None:
        self.model = model

    @sqlalchemy_universal_decorator
    async def fetch_all_from_db(
        self,
        session: AsyncSession,
    ) -> list[T]:
        stmt = select(self.model)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @sqlalchemy_universal_decorator
    async def create_all_objects(
        self,
        session: AsyncSession,
        objects: list[T],
    ) -> list[T]:
        session.add_all(objects)
        await session.flush()
        return objects

    @sqlalchemy_universal_decorator
    async def create_or_update_object(
        self,
        session: AsyncSession,
        object: T,
    ) -> T:
        obj = await session.merge(object)
        await session.flush()
        return obj
