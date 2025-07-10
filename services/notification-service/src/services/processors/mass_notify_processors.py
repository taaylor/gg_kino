import asyncio
import logging

from core.config import app_config
from db.postgres import get_session_context
from services.repository.notification_repository import (
    NotificationRepository,
    get_notification_repository,
)

logger = logging.getLogger(__name__)


class MassNotifyStatusProcessor:
    """Процессор распределения статуса массовых уведомлений."""

    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository

    async def process_mass_notify_new_status(self) -> None:
        """Запускает процесс обработки массовых уведомлений в статусе NEW."""

        while True:  # noqa: WPS457
            async with get_session_context() as session:
                result = await self.repository.update_new_mass_notifications(
                    session, limit=app_config.single_notify_batch
                )
                if result:
                    cnt_notify, sending, delay = result
                    logger.info(
                        f"Изменение статуса массовых уведомлений: {cnt_notify}, \
                            перемещены в ожидании: {delay}, в процессе отправки: {sending}"
                    )
            await asyncio.sleep(app_config.start_processing_interval_sec)

    async def process_mass_notify_delayed_status(self) -> None:
        """Запускает процесс обработки массовых уведомлений в статусе DELAYED."""

        logger.info("Запущен процесс обработки массовых уведомлений в статусе DELAYED")
        while True:  # noqa: WPS457
            async with get_session_context() as session:
                mass_notify = await self.repository.update_delayed_mass_notifications(
                    session, limit=app_config.single_notify_batch
                )
                logger.info(
                    f"Изменение статуса массовых уведомлений c DELAYED в SENDING: {mass_notify}"
                )
                logger.info(
                    "Процесс обработки массовых уведомлений (со статусом DELAYED) \
                    завершен, ждем следующего запуска..."
                )
            await asyncio.sleep(app_config.start_processing_interval_sec)


async def get_mass_notify_status_processor() -> MassNotifyStatusProcessor:
    """Создает и возвращает экземпляр MassNotifyStatusProcessor."""
    repository = get_notification_repository()
    return MassNotifyStatusProcessor(repository)
