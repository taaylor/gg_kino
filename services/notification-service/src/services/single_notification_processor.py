import asyncio
import logging

from db.postgres import get_session_context
from services.repository.notification_repository import (
    NotificationRepository,
    get_notification_repository,
)

logger = logging.getLogger(__name__)


class NewNotificationProcessor:

    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    async def process_new_notifications(self):
        while True:  # noqa: WPS457
            logger.info("Запущен процесс обработки нотификаций в статусе NEW")

            async with get_session_context() as session:
                records = await self.repository.fetch_new_notifications(session)
                if records:
                    logger.info(f"Из БД получено: {len(records)} новых уведомлений")

            await asyncio.sleep(10)


def get_new_notification_processor() -> NewNotificationProcessor:
    repository = get_notification_repository()
    return NewNotificationProcessor(repository=repository)
