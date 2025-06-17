from typing import Sequence

from services.auth_repository import AuthRepository
from services.session_maker import SessionMaker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.decorators import sqlalchemy_universal_decorator


class BaseService:
    """Базовый класс для бизнес-логика для работы с моделями."""

    model = None

    @classmethod
    @sqlalchemy_universal_decorator
    async def find_one_or_none(
        cls,
        session: AsyncSession,
        *where_args,
        options: Sequence = (),
    ):
        """Выполняет SELECT с условием и возвращает одну запись или None.

        Аргументы должны передаваться строго позиционно:
        сначала session, затем условия (where).
        К примеру:
        UserService.find_one_or_none(
                session,
                User.id == request_body.id
            )
        """
        query = select(cls.model).where(*where_args)
        if options:
            query = query.options(*options)
        exequted_query = await session.execute(query)
        return exequted_query.scalar_one_or_none()


class MixinAuthRepository:
    def __init__(self, repository: AuthRepository, session: AsyncSession):
        self.repository = repository
        self.session = session


class BaseAuthService(MixinAuthRepository):
    def __init__(
        self,
        repository: AuthRepository,
        session: AsyncSession,
        session_maker: SessionMaker,
    ):
        super().__init__(repository, session)
        self.session_maker = session_maker
