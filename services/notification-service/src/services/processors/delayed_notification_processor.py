import asyncio
import logging
from typing import NoReturn

from core.config import app_config
from db.postgres import get_session_context
from models.enums import NotificationStatus
from services.processors.sender import NotificationSender, get_notification_sender
from services.repository.notification_repository import (
    NotificationRepository,
    get_notification_repository,
)

logger = logging.getLogger(__name__)


class DelayedNotificationProcessor:  # noqa: WPS214

    __slots__ = (
        "repository",
        "sender",
    )

    def __init__(
        self,
        repository: NotificationRepository,
        sender: NotificationSender,
    ) -> None:
        self.repository = repository
        self.sender = sender

    async def process_delayed_notifications(self) -> NoReturn:  # noqa: WPS210, WPS217
        while True:  # noqa: WPS457
            logger.info(
                f"Запущен процесс обработки нотификаций в статусе {NotificationStatus.DELAYED}"
            )

            async with get_session_context() as session:
                while notifications := await self.repository.fetch_delayed_notifications(  # noqa: WPS332, E501
                    session, limit=app_config.single_notify_batch
                ):

                    logger.info(f"Отложенных уведомлений в процессе отправки в очередь: {len(notifications)}")  # type: ignore # noqa: E501
                    sending_failed, sent_to_queue = await self.sender.push_to_queue(notifications)  # type: ignore # noqa: E501
                    sending_result = sending_failed + sent_to_queue
                    await self.repository.update_notifications(
                        session=session, notifications=sending_result
                    )

            await asyncio.sleep(app_config.start_processing_interval_sec)


async def get_delayed_notification_processor() -> DelayedNotificationProcessor:
    repository = get_notification_repository()
    sender = await get_notification_sender()
    return DelayedNotificationProcessor(repository=repository, sender=sender)
