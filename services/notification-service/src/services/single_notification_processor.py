import asyncio
import logging
from uuid import UUID

from core.config import app_config
from db.postgres import get_session_context
from models.logic_models import UserProfile
from models.models import Notification
from services.repository.notification_repository import (
    NotificationRepository,
    get_notification_repository,
)
from suppliers.user_profile_supplier import ProfileSupplier, get_profile_supplier

logger = logging.getLogger(__name__)


class NewNotificationProcessor:  # noqa: WPS214

    def __init__(self, repository: NotificationRepository, supplier: ProfileSupplier):
        self.repository = repository
        self.supplier = supplier

    async def process_new_notifications(self):  # noqa: WPS210
        while True:  # noqa: WPS457
            logger.info("Запущен процесс обработки нотификаций в статусе NEW")

            async with get_session_context() as session:
                while (
                    notifications := await self.repository.fetch_new_notifications(  # noqa: WPS332
                        session, limit=app_config.single_notify_batch
                    )
                ):

                    logger.info(f"Из БД получено: {len(notifications)} новых уведомлений")
                    user_ids = [notification.user_id for notification in notifications]
                    profiles = await self._fetch_profiles(user_ids)

                    enrich_failed_notifications, enriched_notifications = (
                        await self._enrich_notifications(notifications, profiles)
                    )

                    logger.info(
                        f"Получилось обогатить: {len(enriched_notifications)}, "
                        f"не нашлось профилей для: {len(enrich_failed_notifications)} уведомлений"
                    )

                    await self._push_to_queue(enriched_notifications)

            await asyncio.sleep(10)

    async def _fetch_profiles(self, user_ids: list[UUID]) -> list[UserProfile]:
        try:
            profiles = await self.supplier.fetch_profiles(user_ids=user_ids)
            logger.debug(f"Получено: {len(profiles)} профилей для отправки уведомлений")
            return profiles
        except Exception:
            logger.warning(f"Не удалось получить профили для: {user_ids}")
            return []

    async def _enrich_notifications(
        self, notifications: list[Notification], profiles: list[UserProfile]
    ) -> tuple[list[Notification], list[Notification]]:
        enriched_notifications: list[Notification] = []
        enrich_failed_notifications: list[Notification] = []
        # Преобразую в dict чтобы сложность сопоставления нотификации и
        # профиля была O(m + n), а не O(m * n) (т.к. перебор двух списков отстой)
        profiles_dict = {profile.user_id: profile for profile in profiles}

        for notify in notifications:
            user_profile = profiles_dict.get(notify.user_id)

            if not user_profile:
                logger.warning(f"Не удалось обогатить нотификацию {notify.id}")
                enrich_failed_notifications.append(notify)
                continue

            notify.user_timezone = user_profile.user_timezone
            notify.event_data.update(
                {
                    "first_name": user_profile.first_name,
                    "last_name": user_profile.last_name,
                    "gender": user_profile.gender,
                    "email": user_profile.email,
                    "is_fictional_email": user_profile.is_fictional_email,
                    "is_email_notify_allowed": user_profile.is_email_notify_allowed,
                    "is_verified_email": user_profile.is_verified_email,
                    "created_at": user_profile.is_verified_email,
                }
            )

            enriched_notifications.append(notify)
        return enrich_failed_notifications, enriched_notifications

    async def _push_to_queue(self, notifications: list[Notification]):
        """Функция отправляет уведомление в очередь отправки"""
        await asyncio.sleep(2)

    async def _set_failed_status(self, notifications: list[Notification]):
        """Функция возвращает уведомление БД в результате ошибки обогащения"""
        await asyncio.sleep(2)

    async def _sort_by_sending_time(self, notifications: list[Notification]):
        """Функция проверяет необходимость отправки уведомления прямо сейчас"""
        await asyncio.sleep(2)

    async def _delayed_returns_to_db(self, notifications: list[Notification]):
        """Функция возвращает в БД уведомления, отправку которых нужно отложить"""
        await asyncio.sleep(2)


def get_new_notification_processor() -> NewNotificationProcessor:
    repository = get_notification_repository()
    supplier = get_profile_supplier()
    return NewNotificationProcessor(repository=repository, supplier=supplier)
