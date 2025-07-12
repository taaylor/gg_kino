from db.postgres import Base
from sqlalchemy.ext.asyncio import AsyncSession
from utils.decorators import sqlalchemy_universal_decorator


class BaseRepository[T: Base]:
    """Базовый репозиторий для работы с хранилищем данных."""

    @sqlalchemy_universal_decorator
    async def create_object(
        self,
        session: AsyncSession,
        object: T,
    ) -> T:
        session.add(object)
        await session.flush()
        return object

    @sqlalchemy_universal_decorator
    async def update_object(
        self,
        session: AsyncSession,
        object: T,
    ) -> T:
        obj = await session.merge(object)
        await session.flush()
        return obj
