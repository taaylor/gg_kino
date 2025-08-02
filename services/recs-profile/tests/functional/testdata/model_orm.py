import uuid
from datetime import datetime

from sqlalchemy import ARRAY, Float, String, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from tests.functional.testdata.model_enum import RecsSourceType


class Base(AsyncAttrs, DeclarativeBase):

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )


class UserRecs(Base):
    """Экземпляры рекомендаций для пользователя"""

    __tablename__ = "user_recs"
    __table_args__ = {"schema": "recs_profile"}

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, comment="Уникальный идентификатор рекомендации."
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        index=True, comment="ID пользователя, для которого сохранена рекомендация."
    )
    film_id: Mapped[uuid.UUID] = mapped_column(
        comment="Идентификатор фильма, по которому была сохранена рекомендация."
    )
    rec_source_type: Mapped[RecsSourceType] = mapped_column(
        String(100), comment="Событие, вызвавшее создание рекомендации."
    )
    embedding: Mapped[list | None] = mapped_column(
        ARRAY(Float), comment="Эмбеддинг, полученный в результате обработки запроса."
    )
