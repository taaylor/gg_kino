from services.auth_repository import AuthReository
from services.session_maker import SessionMaker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    """
    Базовый класс для бизнес-логика для работы с моделями.
    """

    model = None

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


class BaseAuthService:
    def __init__(
        self, repository: AuthReository, session: AsyncSession, session_maker: SessionMaker
    ):
        self.repository = repository
        self.session = session
        self.session_maker = session_maker
