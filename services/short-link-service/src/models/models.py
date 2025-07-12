import logging
import uuid
from datetime import datetime

from db.postgres import Base
from sqlalchemy import TIMESTAMP, BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

logger = logging.getLogger(__name__)


class ShortLink(Base):
    """Экземпляры коротких ссылок"""

    __tablename__ = "short_link"
    __table_args__ = {"schema": "link"}

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Уникальный идентификатор экземпляра короткой ссылки",
    )
    original_url: Mapped[str] = mapped_column(String(3000), comment="Оригинальная ссылка")
    short_url: Mapped[str] = mapped_column(
        String(3000), comment="Сокращённая ссылка", index=True, unique=True
    )
    short_path: Mapped[str] = mapped_column(
        String(50), index=True, unique=True, comment="Префикс для короткой ссылки"
    )
    valid_to: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        comment="Дата до которой валидна короткая ссылка",
    )
    is_archive: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Флаг архивности короткой ссылки"
    )
    uses_count: Mapped[int] = mapped_column(
        BigInteger, default=0, comment="Количество использований ссылки"
    )
