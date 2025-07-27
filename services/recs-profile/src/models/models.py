import logging
import uuid

from db.postgres import Base
from models.enums import ProcessingStatus
from sqlalchemy import ARRAY, Float, String
from sqlalchemy.dialects.postgresql import JSONB
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
    query: Mapped[str] = mapped_column(
        String(1000), comment="Текст пользовательского запроса рекомендации"
    )
    processing_result: Mapped[ProcessingStatus] = mapped_column(
        String(100), comment="Результат обработки"
    )
    llm_resp: Mapped[dict] = mapped_column(JSONB, comment="Ответ LLM")
    final_embedding: Mapped[list | None] = mapped_column(
        ARRAY(Float), comment="Эмбеддинг, полученный в результате обработки запроса"
    )
