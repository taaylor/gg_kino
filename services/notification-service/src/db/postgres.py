import logging
from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

logger = logging.getLogger(__name__)


# Базовый класс для всех моделей
class Base(AsyncAttrs, DeclarativeBase):
    """AsyncAttrs: Позволяет создавать асинхронные модели, что улучшает
    производительность при работе с асинхронными операциями.

    __abstract__ = True - абстрактный класс, чтобы не создавать отдельную таблицу для него

    Mapped — это современный способ аннотировать типы данных для колонок в моделях SQLAlchemy.

    mapped_column — это функция, которая используется для создания колонок в моделях SQLAlchemy.
    Она принимает в качестве аргументов тип данных колонки и дополнительные параметры,
    такие как primary_key, nullable, default и так далее
    """

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )


async_session_maker: async_sessionmaker | None = None


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if async_session_maker is None:
        raise ValueError("[PostgreSQL] sessionmaker не инициализирован")
    async with async_session_maker() as session:
        yield session


def get_session_context():
    """Возвращает контекстный менеджер для использования вне FastAPI"""
    if async_session_maker is None:
        raise ValueError("[PostgreSQL] sessionmaker не инициализирован")
    return async_session_maker()
