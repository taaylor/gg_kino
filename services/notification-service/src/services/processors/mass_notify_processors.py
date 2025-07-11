import asyncio
import datetime
import logging
from zoneinfo import ZoneInfo

from core.config import app_config
from db.cache import Cache, get_cache
from db.postgres import get_session_context
from models.enums import MassNotificationStatus
from models.models import MassNotification, Notification
from services.repository.notification_repository import (
    NotificationRepository,
    get_notification_repository,
)
from suppliers.user_profile_supplier import ProfileSupplier, get_profile_supplier

logger = logging.getLogger(__name__)


class MassNotifyStatusProcessor:
    """Процессор распределения статуса массовых уведомлений."""

    __slots__ = ("repository",)

    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository

    async def process_mass_notify_new_status(self) -> None:
        """Запускает процесс обработки массовых уведомлений в статусе NEW."""

        while True:  # noqa: WPS457
            async with get_session_context() as session:
                result = await self.repository.update_new_mass_notifications(
                    session, limit=app_config.mass_notify_batch
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
        while True:  # noqa: WPS457
            logger.info("Запущен процесс обработки массовых уведомлений в статусе DELAYED")
            async with get_session_context() as session:
                while mass_notify := await self.repository.update_delayed_mass_notifications(  # noqa: WPS332, E501
                    session, limit=app_config.mass_notify_batch
                ):

                    logger.info(
                        f"Изменение статуса массовых уведомлений c DELAYED в SENDING: {mass_notify}"
                    )
                    logger.info(
                        "Процесс обработки массовых уведомлений (со статусом DELAYED) \
                        завершен, ждем следующего запуска..."
                    )
            await asyncio.sleep(app_config.start_processing_interval_sec)


class MassNotifyETLProcessor:
    """ "Процесс ETL который разбивает массовые уведомления на отдельные уведомления."""

    __slots__ = ("repository", "cache", "prof_supplier")

    def __init__(
        self, repository: NotificationRepository, cache: Cache, prof_supplier: ProfileSupplier
    ) -> None:

        self.repository = repository
        self.cache = cache
        self.prof_supplier = prof_supplier

    async def process_mass_notify_etl(self) -> None:
        """Запускает процесс ETL для массовых уведомлений."""

        while True:  # noqa: WPS457
            logger.info("Запущен процесс ETL для массовых уведомлений")
            async with get_session_context() as session:
                while mass_notifications := await self.repository.fetch_mass_notification(  # noqa: WPS332, E501
                    session, limit=app_config.mass_notify_batch
                ):
                    tasks = (
                        asyncio.create_task(self._process_one_mass_notify(notify))
                        for notify in mass_notifications
                    )
                    # включаем конкурентность для быстрого выполнения
                    await asyncio.gather(*tasks)
            await asyncio.sleep(app_config.start_processing_interval_sec)

    async def _process_one_mass_notify(self, notify: MassNotification):  # noqa: WPS217
        """Обрабатывает одно массовое уведомление, разбивая его на отдельные уведомления."""

        cache_key = f"page_number_mass_notify:{notify.id}"
        page_number = await self.cache.get(cache_key)
        if page_number is None:
            page_number = 1  # type: ignore

        async with get_session_context() as session:

            profiles = await self.prof_supplier.fetch_all_profiles(
                page_number=page_number, page_size=app_config.profile_page_size
            )

            single_notifications = [
                Notification(
                    user_id=profile.user_id,
                    method=notify.method,
                    source=notify.source,
                    target_sent_at=notify.target_start_sending_at,
                    priority=notify.priority,
                    event_type=notify.event_type,
                    event_data=notify.event_data,
                    template_id=notify.template_id,
                    mass_notification_id=notify.id,
                )
                for profile in profiles.profiles
            ]

            await self.repository.create_all_objects(session, single_notifications)
            logger.info(
                f"Создано {len(single_notifications)} уведомлений из "
                f"массового уведомления: {notify.id}"
            )
            if len(profiles.profiles) < app_config.profile_page_size:  # проверка
                logger.info(
                    f"Массовое уведомление {notify.id} обработано полностью, \
                    больше нет профилей для обработки."
                )
                notify.status = MassNotificationStatus.SENT
                notify.actual_sent_at = datetime.datetime.now(ZoneInfo("UTC"))
                await self.repository.create_or_update_object(session, notify)
                await self.cache.destroy(cache_key)
            else:
                logger.info(f"Массовое уведомление {notify.id} обработано частично")
                await self.cache.set(
                    cache_key,
                    str(page_number + 1),  # type: ignore
                    expire=app_config.expire_cache_sec,
                )


def get_mass_notify_status_processor() -> MassNotifyStatusProcessor:
    """Создает и возвращает экземпляр MassNotifyStatusProcessor."""
    repository = get_notification_repository()
    return MassNotifyStatusProcessor(repository)


async def get_mass_notify_etl_processor() -> MassNotifyETLProcessor:
    """Создает и возвращает экземпляр MassNotifyETLProcessor."""
    repository = get_notification_repository()
    cache = await get_cache()
    prof_supplier = get_profile_supplier()
    return MassNotifyETLProcessor(repository, cache, prof_supplier)
