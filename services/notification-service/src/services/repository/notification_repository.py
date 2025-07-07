import logging
from datetime import datetime
from functools import lru_cache
from uuid import UUID
from zoneinfo import ZoneInfo

from models.enums import NotificationStatus
from models.models import Notification
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from utils.decorators import sqlalchemy_universal_decorator

logger = logging.getLogger(__name__)


class NotificationRepository:

    @sqlalchemy_universal_decorator
    async def create_new_notification(
        self, session: AsyncSession, notification: Notification
    ) -> Notification:
        session.add(notification)
        await session.flush()
        return notification

    @sqlalchemy_universal_decorator
    async def fetch_new_notifications(
        self, session: AsyncSession, limit: int = 10
    ) -> list[Notification]:
        """Получает новые уведомления и сразу меняет их статус на PROCESSING"""
        stmt = (
            select(Notification)
            .where(Notification.status == NotificationStatus.NEW)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await session.execute(stmt)
        db_notifications = list(result.scalars().all())

        # Сразу меняем статус, чтобы другие процессы их не взяли
        for notify in db_notifications:
            notify.status = NotificationStatus.PROCESSING

        await session.flush()
        return db_notifications

    @sqlalchemy_universal_decorator
    async def fetch_delayed_notifications(
        self, session: AsyncSession, limit: int = 10
    ) -> list[Notification]:
        """Получает отложенные уведомления и сразу меняет их статус на PROCESSING"""
        now_utc = datetime.now(ZoneInfo("UTC"))
        stmt = (
            select(Notification)
            .where(
                Notification.status == NotificationStatus.DELAYED,
                Notification.target_sent_at <= now_utc,
            )
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await session.execute(stmt)
        db_notifications = list(result.scalars().all())

        # Сразу меняем статус, чтобы другие процессы их не взяли
        for notify in db_notifications:
            notify.status = NotificationStatus.PROCESSING

        await session.flush()
        return db_notifications

    @sqlalchemy_universal_decorator
    async def update_notifications(  # noqa: WPS210
        self, session: AsyncSession, notifications: list[Notification]
    ) -> None:
        """Полностью обновляет уведомление в БД на то состояние, которое пришло в запросе"""
        notify_ids = [notify.id for notify in notifications]
        stmt = select(Notification).where(Notification.id.in_(notify_ids))
        result = await session.execute(stmt)
        db_notifications = result.scalars().all()

        notifications_dict = {notify.id: notify for notify in notifications}

        updated_count = 0
        for notify in db_notifications:
            updated_notify = notifications_dict[notify.id]
            for attr_name in updated_notify.__table__.columns.keys():
                if attr_name != "id":  # id не обновляем
                    setattr(notify, attr_name, getattr(updated_notify, attr_name))
            updated_count += 1

            # Принудительно помечаем JSON поле как измененное иначе sqlalchemy его не обновит
            flag_modified(notify, "event_data")

        await session.flush()
        logger.info(f"Обновлено {updated_count} уведомлений")

    @sqlalchemy_universal_decorator
    async def update_notification_status_by_id(
        self, session: AsyncSession, notify_ids: list[UUID], status: NotificationStatus
    ) -> list[Notification]:
        """ "Обновляет статус уведомления в БД в результате обработки коллбека по отправке"""
        now_utc = datetime.now(ZoneInfo("UTC"))
        stmt = select(Notification).where(Notification.id.in_(notify_ids))
        result = await session.execute(stmt)
        db_notifications = list(result.scalars().all())

        for notify in db_notifications:
            notify.status = status
            notify.actual_sent_at = now_utc
        await session.flush()

        return db_notifications


@lru_cache
def get_notification_repository() -> NotificationRepository:
    return NotificationRepository()
