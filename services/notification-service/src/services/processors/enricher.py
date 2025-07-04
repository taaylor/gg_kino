import logging
from uuid import UUID

from models.enums import NotificationStatus
from models.logic_models import UserProfile
from models.models import Notification
from suppliers.user_profile_supplier import ProfileSupplier, get_profile_supplier

logger = logging.getLogger(__name__)


class NotificationEnricher:
    """Обогащает экземпляры уведомлений дополнительными атрибутами
    для отправки персональных уведомлений"""

    # TODO: Добавить разное обогащение для разных типов уведомлений

    __slots__ = ("supplier",)

    def __init__(self, supplier: ProfileSupplier) -> None:
        self.supplier = supplier

    async def enrich_notifications(  # noqa: WPS210
        self, notifications: list[Notification]
    ) -> tuple[list[Notification], list[Notification]]:
        enriched_notifications: list[Notification] = []
        enrich_failed_notifications: list[Notification] = []

        user_ids = [notification.user_id for notification in notifications]
        profiles = await self._fetch_profiles(user_ids)

        # Преобразую в dict чтобы сложность сопоставления нотификации и
        # профиля была O(m + n), а не O(m * n) (т.к. перебор двух списков отстой)
        profiles_dict = {profile.user_id: profile for profile in profiles}

        for notify in notifications:
            user_profile = profiles_dict.get(notify.user_id)

            if not user_profile:
                logger.warning(f"Не удалось обогатить нотификацию {notify.id}")
                notify.status = NotificationStatus.PROCESSING_ERROR
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

    async def _fetch_profiles(self, user_ids: list[UUID]) -> list[UserProfile]:
        try:
            profiles = await self.supplier.fetch_profiles(user_ids=user_ids)
            logger.debug(f"Получено: {len(profiles)} профилей для отправки уведомлений")
            return profiles
        except Exception:
            logger.warning(f"Не удалось получить профили для: {user_ids}")
            return []


def get_notification_enricher() -> NotificationEnricher:
    supplier = get_profile_supplier()
    return NotificationEnricher(supplier=supplier)
