import logging
import uuid

from db.postgres import Base
from models.enums import RecsSourceType
from sqlalchemy import ARRAY, Float, String
from sqlalchemy.orm import Mapped, mapped_column

logger = logging.getLogger(__name__)


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
