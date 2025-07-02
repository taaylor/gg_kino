import asyncio
import logging

from db.postgres import get_session_context
from services.repository.notification_repository import (
    NotificationRepository,
    get_notification_repository,
)
from suppliers.user_profile_supplier import ProfileSupplier, get_profile_supplier

logger = logging.getLogger(__name__)


class NewNotificationProcessor:

    def __init__(self, repository: NotificationRepository, supplier: ProfileSupplier):
        self.repository = repository
        self.supplier = supplier

    async def process_new_notifications(self):
        while True:  # noqa: WPS457
            logger.info("Запущен процесс обработки нотификаций в статусе NEW")

            async with get_session_context() as session:
                records = await self.repository.fetch_new_notifications(session)
                if records:  # noqa: WPS220
                    logger.info(f"Из БД получено: {len(records)} новых уведомлений")  # noqa: WPS220

                    # Испытания
                    user_id = records[0].user_id  # noqa: WPS220
                    try:  # noqa: WPS220
                        profile = await self.supplier.fetch_profile(user_id=user_id)  # noqa: WPS220
                        logger.debug(  # noqa: WPS220
                            f"Получен профиль пользователя для уведомления: {profile}"
                        )
                    except Exception:
                        logger.warning(  # noqa: WPS220
                            f"Не удалось получить профиль для: {user_id}"
                        )

            await asyncio.sleep(10)


def get_new_notification_processor() -> NewNotificationProcessor:
    repository = get_notification_repository()
    supplier = get_profile_supplier()
    return NewNotificationProcessor(repository=repository, supplier=supplier)
