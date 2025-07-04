import asyncio
import logging

from core.config import app_config
from db.postgres import get_session_context
from models.models import Notification
from services.processors.enricher import NotificationEnricher, get_notification_enricher
from services.processors.sender import NotificationSender, get_notification_sender
from services.processors.timezone_manager import TimeZoneManager, get_timezone_manager
from services.repository.notification_repository import (
    NotificationRepository,
    get_notification_repository,
)

logger = logging.getLogger(__name__)


class NewNotificationProcessor:  # noqa: WPS214

    __slots__ = ("repository", "supplier", "enricher", "sender", "tz_manager")

    def __init__(
        self,
        repository: NotificationRepository,
        enricher: NotificationEnricher,
        sender: NotificationSender,
        tz_manager: TimeZoneManager,
    ):
        self.repository = repository
        self.enricher = enricher
        self.sender = sender
        self.tz_manager = tz_manager

    async def process_new_notifications(self):  # noqa: WPS210, WPS217
        while True:  # noqa: WPS457
            logger.info("Запущен процесс обработки нотификаций в статусе NEW")

            async with get_session_context() as session:
                while (
                    notifications := await self.repository.fetch_new_notifications(  # noqa: WPS332
                        session, limit=app_config.single_notify_batch
                    )
                ):

                    logger.info(f"Из БД получено: {len(notifications)} новых уведомлений")

                    enrich_failed_notifications, enriched_notifications = (
                        await self.enricher.enrich_notifications(notifications)
                    )

                    logger.info(
                        f"Получилось обогатить: {len(enriched_notifications)}, "
                        f"не нашлось профилей для: {len(enrich_failed_notifications)} уведомлений"
                    )

                    # Сортируем уведомления по времени отправки
                    send_now, send_later = await self.tz_manager.sort_by_sending_time(
                        enriched_notifications
                    )

                    # Отправляем уведомления, которые можно отправить сейчас
                    if send_now:
                        await self.sender._push_to_queue(send_now)  # noqa: WPS220

                    # Возвращаем в БД уведомления для отложенной отправки
                    if send_later:
                        await self.repository.update_delayed_notifications(  # noqa: WPS220
                            session=session, notifications=send_later
                        )
                        logger.info(  # noqa: WPS220
                            f"Уведомлений отложено для будущей отправки: {len(send_later)}"
                        )

                    # Устанавливаем статус "неудачно" для уведомлений, которые не удалось обогатить
                    if enrich_failed_notifications:
                        await self._set_failed_status(enrich_failed_notifications)  # noqa: WPS220

            await asyncio.sleep(10)

    async def _set_failed_status(self, notifications: list[Notification]):
        """Функция возвращает уведомление БД в результате ошибки обогащения"""
        await asyncio.sleep(2)


def get_new_notification_processor() -> NewNotificationProcessor:
    repository = get_notification_repository()
    enricher = get_notification_enricher()
    sender = get_notification_sender()
    tz_manager = get_timezone_manager()
    return NewNotificationProcessor(
        repository=repository, enricher=enricher, sender=sender, tz_manager=tz_manager
    )
