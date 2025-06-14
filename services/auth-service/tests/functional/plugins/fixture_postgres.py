import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from tests.functional.core.settings import test_conf
from tests.functional.testdata.model_orm import Base


@pytest_asyncio.fixture(name="async_session_maker", scope="session")
async def async_session_maker():
    engine = create_async_engine(test_conf.postgres.ASYNC_DATABASE_URL, future=True)
    async_session_maker = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    yield async_session_maker

    await engine.dispose()


@pytest_asyncio.fixture(name="pg_session")
async def pg_session(async_session_maker: sessionmaker):
    async with async_session_maker() as session:
        await session.begin()  # Открываем транзакцию

        yield session

        # очищаем таблицы после транзакции

        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()
