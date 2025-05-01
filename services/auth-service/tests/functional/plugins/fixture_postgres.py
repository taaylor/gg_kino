from typing import AsyncGenerator

from pytest import fixture
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from tests.functional.core.settings import test_conf

engine = create_async_engine(test_conf.postgres.ASYNC_DATABASE_URL, echo=True, future=True)


@fixture(name="async_session_maker", scope="session")
async def async_session_maker_fixture():
    session_maker = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield session_maker


@fixture(name="pg_session")
async def pg_session(async_session_maker) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            # опционально: откатить, чтобы тесты не влияли друг на друга
            await session.rollback()
