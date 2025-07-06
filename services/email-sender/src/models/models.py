import logging
import uuid

from db.postgres import Base
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

logger = logging.getLogger(__name__)


class Template(Base):
    __tablename__ = "template"
    __table_args__ = {"schema": "email_sender"}

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Уникальный идентификатор шаблона",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="HTML код шаблона",
    )

    def __str__(self):
        return f"Модель: {self.__class__.__name__}(id={self.id}, username={self.username})"
