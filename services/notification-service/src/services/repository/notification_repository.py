import logging
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.models import Notification
from models.enums import NotificationStatus
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
    async def fetch_new_notifications(self, session: AsyncSession) -> list[Notification]:
        stmt = select(Notification).where(Notification.status == NotificationStatus.NEW)
        result = await session.execute(stmt)
        return list(result.scalars().all())


@lru_cache
def get_notification_repository() -> NotificationRepository:
    return NotificationRepository()
