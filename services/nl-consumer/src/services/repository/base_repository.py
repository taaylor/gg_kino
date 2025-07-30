from db.postgres import Base
from sqlalchemy.ext.asyncio import AsyncSession
from utils.decorators import sqlalchemy_universal_decorator


class BaseRepository[T: Base]:
    """Базовый репозиторий для работы с хранилищем данных."""

    def __init__(self, model: type[T]) -> None:
        self.model = model

    @sqlalchemy_universal_decorator
    async def create_entity(
        self,
        session: AsyncSession,
        entity: T,
    ) -> T:
        session.add(entity)
        await session.flush()
        return entity
