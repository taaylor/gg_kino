from datetime import datetime

import pytest_asyncio
from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from tests.functional.core.settings import test_conf


# Базовый класс для всех моделей
class Base(AsyncAttrs, DeclarativeBase):
    """
    AsyncAttrs: Позволяет создавать асинхронные модели, что улучшает
    производительность при работе с асинхронными операциями.

    __abstract__ = True - абстрактный класс, чтобы не создавать отдельную таблицу для него

    Mapped — это современный способ аннотировать типы данных для колонок в моделях SQLAlchemy.

    mapped_column — это функция, которая используется для создания колонок в моделях SQLAlchemy.
    Она принимает в качестве аргументов тип данных колонки и дополнительные параметры,
    такие как primary_key, nullable, default и так далее
    """

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


@pytest_asyncio.fixture(name="async_session_maker", scope="session")
async def async_session_maker():
    engine = create_async_engine(test_conf.postgres.ASYNC_DATABASE_URL, echo=True, future=True)
    async_session_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    # создание таблиц перед открытием соединения не требуется,
    # так как они создаются с помощью миграций в API

    yield async_session_maker

    # дропаем все таблицы после завершения всех тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(name="pg_session")
def pg_session(async_session_maker):
    async def inner():
        async with async_session_maker() as session:
            await session.begin()  # Открываем транзакцию
            try:
                yield session
            finally:
                await session.rollback()
                # очищаем таблицы после транзакции
                for table in reversed(Base.metadata.sorted_tables):
                    await session.execute(text(f"TRUNCATE {table.name} CASCADE;"))

    return inner
