import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from core.config import app_config
from db.rabbitmq import AsyncProducer, get_producer
from models.enums import EventType, NotificationStatus
from models.logic_models import NotificationLogic
from models.models import Notification

logger = logging.getLogger(__name__)


class NotificationSender:

    __slots__ = ("queue_producer",)

    def __init__(self, queue_producer: AsyncProducer) -> None:
        self.queue_producer = queue_producer

    async def push_to_queue(  # noqa: WPS210, WPS213, WPS231
        self, notifications: list[Notification]
    ) -> tuple[list[Notification], list[Notification]]:
        """Функция отправляет уведомление в очередь отправки"""
        type_counts: dict[EventType, int] = {}

        sent_to_queue = []
        sending_failed = []

        for notify in notifications:
            notify_dto = NotificationLogic.model_validate(notify)
            notify_dto.event_type = EventType(notify_dto.event_type)

            try:
                # Подсчет количества сообщений по типам
                type_counts[notify_dto.event_type] = type_counts.get(notify_dto.event_type, 0) + 1

                if notify_dto.event_type == EventType.TEST:
                    logger.info(
                        f"Получено тестовое сообщение {notify_dto.model_dump_json(indent=4)}"
                    )
                if notify_dto.event_type == EventType.USER_REVIEW_LIKED:
                    await self.queue_producer.publish(  # noqa: WPS476
                        queue_name=app_config.rabbit.review_like_queue,
                        message=notify_dto.model_dump_json(),
                    )
                if notify_dto.event_type == EventType.USER_REGISTERED:
                    await self.queue_producer.publish(  # noqa: WPS476
                        queue_name=app_config.rabbit.registered_queue,
                        message=notify_dto.model_dump_json(),
                    )
                if notify_dto.event_type == EventType.AUTO_MASS_NOTIFY:
                    await self.queue_producer.publish(  # noqa: WPS476
                        queue_name=app_config.rabbit.auto_mailing_queue,
                        message=notify_dto.model_dump_json(),
                    )
                if notify_dto.event_type == EventType.MANAGER_MASS_NOTIFY:
                    await self.queue_producer.publish(  # noqa: WPS476
                        queue_name=app_config.rabbit.manager_mailing_queue,
                        message=notify_dto.model_dump_json(),
                    )

                notify.added_queue_at = datetime.now(ZoneInfo("UTC"))
                notify.status = NotificationStatus.SENDING
                sent_to_queue.append(notify)
            except Exception:
                logger.error(f"Ошибка при попытке отправить сообщение: {notify.id} в очередь")
                notify.status = NotificationStatus.PROCESSING_ERROR
                sending_failed.append(notify)

        logger.debug(f"Поступило: {len(notifications)} сообщений для отправки")
        # Логирование количества сообщений по типам
        for event_type, count in type_counts.items():
            logger.info(f"Количество сообщений типа {event_type}: {count}")
        logger.info(
            f"Сообщений отправлено успешно: {len(sent_to_queue)}, "
            f"Возникла ошибка при попытке отправить: {len(sending_failed)}"
        )

        return sending_failed, sent_to_queue


async def get_notification_sender() -> NotificationSender:
    queue_producer = await get_producer()
    return NotificationSender(queue_producer=queue_producer)
