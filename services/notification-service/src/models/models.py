# noqa: WPS432
import logging
import uuid
from datetime import datetime

from db.postgres import Base
from models.enums import MassNotificationStatus, NotificationMethod, NotificationStatus, Priority
from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

logger = logging.getLogger(__name__)


class Notification(Base):
    """Экземпляры уведомлений для пользователей"""

    __tablename__ = "notification"
    __table_args__ = {"schema": "notification"}

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4(), comment="Уникальный идентификатор уведомления"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        comment="ID пользователя, которому предназначено уведомление"
    )
    method: Mapped[NotificationMethod] = mapped_column(
        String(50), comment="Канал отправки уведомления (email, push и т.д.)"
    )
    source: Mapped[str] = mapped_column(
        String(50), comment="Источник события, вызвавшего уведомление"
    )
    status: Mapped[NotificationStatus] = mapped_column(
        String(50), default=NotificationStatus.NEW, comment="Текущее состояние уведомления"
    )
    target_sent_at: Mapped[datetime] = mapped_column(
        DateTime, comment="Планируемое время отправки уведомления"
    )
    actual_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime, comment="Фактическое время отправки уведомления"
    )
    added_queue_at: Mapped[datetime | None] = mapped_column(
        DateTime, comment="Время постановки уведомления в очередь на отправку"
    )
    priority: Mapped[Priority] = mapped_column(
        String(50), default=Priority.LOW, comment="Приоритет уведомления"
    )
    event_data: Mapped[dict | None] = mapped_column(
        JSONB, comment="Дополнительные данные события для шаблона уведомления"
    )
    user_timezone: Mapped[str] = mapped_column(String(50), comment="Часовой пояс пользователя")
    template_id: Mapped[uuid.UUID | None] = mapped_column(comment="ID шаблона уведомления")
    mass_notification_id: Mapped[uuid.UUID] = mapped_column(
        comment="ID массовой рассылки, если уведомление массовое"
    )


class MassNotification(Base):
    """Массовые рассылки"""

    __tablename__ = "mass_notification"
    __table_args__ = {"schema": "notification"}

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4(), comment="Уникальный идентификатор массовой рассылки"
    )
    method: Mapped[NotificationMethod] = mapped_column(
        String(50), comment="Канал отправки уведомлений (email, push и т.д.)"
    )
    source: Mapped[str] = mapped_column(String(50), comment="Источник события, вызвавшего рассылку")
    status: Mapped[MassNotificationStatus] = mapped_column(
        String(50), default=MassNotificationStatus.NEW, comment="Текущее состояние рассылки"
    )
    target_start_sending_at: Mapped[datetime] = mapped_column(
        DateTime, comment="Планируемое время начала рассылки"
    )
    start_sending_at: Mapped[datetime | None] = mapped_column(
        DateTime, comment="Фактическое время начала рассылки"
    )
    actual_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime, comment="Фактическое время завершения рассылки"
    )
    priority: Mapped[Priority] = mapped_column(
        String(50), default=Priority.LOW, comment="Приоритет рассылки"
    )
    event_data: Mapped[dict] = mapped_column(
        JSONB, comment="Дополнительные данные события для шаблона рассылки"
    )
    template_id: Mapped[uuid.UUID | None] = mapped_column(comment="ID шаблона рассылки")
