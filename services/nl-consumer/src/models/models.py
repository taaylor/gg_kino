import logging
import uuid

from db.postgres import Base
from sqlalchemy.orm import Mapped, mapped_column

logger = logging.getLogger(__name__)


class ProcessedNpl(Base):
    """Экземпляры пользовательских запросов nlp"""

    __tablename__ = "processed_npl"
    __table_args__ = {"schema": "nlp"}

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, comment="Уникальный идентификатор уведомления"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        comment="ID пользователя, которому предназначено уведомление"
    )
