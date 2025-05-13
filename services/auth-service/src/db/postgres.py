import logging
from datetime import datetime
from typing import AsyncGenerator

from core.config import app_config
from fastapi import HTTPException, status
from sqlalchemy import create_engine, func
from sqlalchemy.exc import IntegrityError, MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# from utils.decorators import backoff

logger = logging.getLogger(__name__)


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


async_session_maker: sessionmaker | None = None


sync_engine = create_engine(app_config.postgres.SYNC_DATABASE_URL)
sync_session_maker = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
)


# @backoff()
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if sessionmaker is None:
        raise ValueError("[PostgreSQL] sessionmaker не инициализирован")
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Нарушение целостности данных: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нарушение уникальности",
            )

        except NoResultFound as e:
            await session.rollback()
            logger.warning(f"Запись не найдена: {e}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запись не найдена")

        except MultipleResultsFound as e:
            await session.rollback()
            logger.error(f"Найдено несколько записей: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка: найдено несколько записей",
            )
