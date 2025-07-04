import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from core.config import app_config
from models.enums import NotificationStatus
from models.models import Notification

logger = logging.getLogger(__name__)


class TimeZoneManager:

    async def sort_by_sending_time(  # noqa: WPS210
        self, notifications: list[Notification]
    ) -> tuple[list[Notification], list[Notification]]:
        """
        Функция проверяет необходимость отправки уведомления прямо сейчас.
        Возвращает кортеж: (уведомления для отправки сейчас, уведомления для отложенной отправки)
        """
        send_now = []
        send_later = []

        # Интервал отправки: с notify_start_hour до notify_end_hour по времени пользователя
        start_hour = app_config.notify_start_hour
        end_hour = app_config.notify_end_hour

        for notification in notifications:
            is_allowed, next_send_time = self._is_in_allowed_time_range(
                notification, start_hour, end_hour
            )
            if is_allowed:
                send_now.append(notification)
            else:
                notification.target_sent_at = next_send_time  # type: ignore
                notification.status = NotificationStatus.DELAYED
                send_later.append(notification)
                logger.debug(f"Уведомление {notification.id} отложено до {next_send_time}")

        logger.info(
            f"Уведомлений для отправки сейчас: {len(send_now)},"
            f"для отложенной отправки: {len(send_later)}"
        )
        return send_now, send_later

    def _is_in_allowed_time_range(  # noqa: WPS210
        self, notification: Notification, start_hour: int, end_hour: int
    ) -> tuple[bool, datetime | None]:
        """
        Проверяет, находится ли текущее время в таймзоне пользователя в разрешенном диапазоне.
        Возвращает кортеж: (можно ли отправить сейчас, время следующей отправки)
        """
        try:
            utc_now = datetime.now(ZoneInfo("UTC"))
            user_timezone = notification.user_timezone
            if not user_timezone:
                logger.warning(f"Таймзона не указана для уведомления {notification.id}, отправляем")
                return True, None

            # Преобразуем UTC время в время пользователя
            user_time = utc_now.astimezone(ZoneInfo(user_timezone))
            current_hour = user_time.hour

            is_allowed = start_hour <= current_hour < end_hour

            logger.debug(
                f"Уведомление {notification.id}: текущее время"
                f"пользователя {user_time.strftime('%H:%M')} "
                f"({user_timezone}), разрешено: {is_allowed}"
            )

            if is_allowed:
                return True, None
            else:
                next_send_time = self._calculate_next_send_time(user_time, start_hour, end_hour)
                # Конвертируем время отправки обратно в UTC для хранения
                next_send_time_utc = next_send_time.astimezone(ZoneInfo("UTC"))
                return False, next_send_time_utc

        except Exception as e:
            logger.error(f"Ошибка при проверке времени для уведомления {notification.id}: {e}")
            return True, None

    def _calculate_next_send_time(
        self, user_time: datetime, start_hour: int, end_hour: int
    ) -> datetime:
        """
        Вычисляет время следующей отправки уведомления в таймзоне пользователя.
        """
        # Создаем время начала отправки на сегодня
        today_start = user_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)

        # Если сейчас еще рано (до start_hour), отправляем сегодня в start_hour
        if user_time.hour < start_hour:
            return today_start

        # Если сейчас уже поздно (после end_hour), отправляем завтра в start_hour
        tomorrow_start = today_start + timedelta(days=1)
        return tomorrow_start


def get_timezone_manager() -> TimeZoneManager:
    return TimeZoneManager()
