import logging
import asyncio
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends

from services.repository.notification_repository import (
    NotificationRepository,
    get_notification_repository,
)
from services.base_service import BaseService
from db.postgres import get_session

logger = logging.getLogger(__name__)


class NewNotificationProcessor:

    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    async def process_new_notifications(self):
        while True:
            logger.info("Запущен процесс обработки нотификаций в статусе NEW")
            
            async for session in get_session():
                records = await self.repository.fetch_new_notifications(session)
                if records:
                    logger.info(f"Из БД получено: {len(records)} новых уведомлений")
                break  # выходим из генератора после одной итерации
                
            await asyncio.sleep(10)


def get_new_notification_processor() -> NewNotificationProcessor:
    repository = get_notification_repository()
    return NewNotificationProcessor(repository=repository)
