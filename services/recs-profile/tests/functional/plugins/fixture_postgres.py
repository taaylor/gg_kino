from typing import Any, AsyncGenerator, Callable, Coroutine
from uuid import UUID

import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from tests.functional.core.settings import test_conf
from tests.functional.testdata.model_orm import Base, UserRecs


@pytest_asyncio.fixture(name="async_session_maker", scope="function")
async def async_session_maker() -> AsyncGenerator[async_sessionmaker[AsyncSession], Any]:
    engine = create_async_engine(test_conf.postgres.ASYNC_DATABASE_URL, future=True)
    async_session_maker = async_sessionmaker[AsyncSession](
        bind=engine,
        expire_on_commit=False,
    )

    yield async_session_maker

    await engine.dispose()


@pytest_asyncio.fixture(name="pg_session", scope="function")
async def pg_session(
    async_session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, Any]:
    async with async_session_maker() as session:
        await session.begin()  # Открываем транзакцию

        yield session

        # очищаем таблицы после транзакции

        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()


@pytest_asyncio.fixture(name="fetch_user_recs")
async def fetch_recs(
    pg_session: AsyncSession,
) -> Callable[[UUID], Coroutine[Any, Any, UserRecs | None]]:
    async def inner(user_id: UUID) -> UserRecs | None:
        stmt = select(UserRecs).where(UserRecs.user_id == user_id)
        result = await pg_session.execute(stmt)
        return result.scalars().one_or_none()

    return inner
