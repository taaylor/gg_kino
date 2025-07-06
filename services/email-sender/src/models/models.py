import logging
import uuid

from db.postgres import Base

# from sqlalchemy import DateTime, ForeignKey, PrimaryKeyConstraint, String, UniqueConstraint, text
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column  # , relationship

# from datetime import datetime


logger = logging.getLogger(__name__)


class Template(Base):
    __tablename__ = "email_template"
    __table_args__ = {"schema": "notification"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    template: Mapped[str] = mapped_column(String(50), unique=True)

    def __str__(self):
        return f"Модель: {self.__class__.__name__}(id={self.id}, username={self.username})"
