from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    """
    Базовый класс для бизнес-логика для работы с моделями.
    """

    model = None

    @classmethod
    async def get_object_or_404(cls, session: AsyncSession, *where_args):
        """
        Возвращает объект по условию или вызывает 404, если не найден.

        Аргументы передаются позиционно: session, затем условия.
        """
        obj = await cls.find_one_or_none(session, *where_args)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{cls.model.__name__} not found",
            )
        return obj

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, *where_args):
        """
        Выполняет SELECT с условием и возвращает одну запись или None.

        Аргументы должны передаваться строго позиционно:
        сначала session, затем условия (where).
        К примеру:
        UserService.find_one_or_none(
                session,
                User.id == request_body.id
            )
        """
        query = select(cls.model).where(*where_args)
        exequted_query = await session.execute(query)
        return exequted_query.scalar_one_or_none()
