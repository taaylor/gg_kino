import logging
from functools import lru_cache

from api.v1.notification.schemas import (
    MassNotificationRequest,
    MassNotificationResponse,
    SingleNotificationRequest,
    SingleNotificationResponse,
    UpdateSendingStatusRequest,
    UpdateSendingStatusResponse,
)
from db.postgres import get_session
from fastapi import Depends, HTTPException, status
from models.enums import NotificationStatus
from models.models import MassNotification, Notification
from services.base_service import BaseService
from services.repository.notification_repository import (
    NotificationRepository,
    get_notification_repository,
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class NotificationService(BaseService):

    async def send_single_notification(
        self, request_body: SingleNotificationRequest
    ) -> SingleNotificationResponse:
        """Сохраняет в БД одну новую нотификацию со статусом NEW"""

        logger.info(
            f"Получен запрос на отправку нотификации: {request_body.model_dump_json(indent=4)}"
        )

        new_notify = Notification(
            user_id=request_body.user_id,
            method=request_body.method,
            source=request_body.source,
            target_sent_at=request_body.target_sent_at,
            priority=request_body.priority,
            event_type=request_body.event_type,
            event_data=request_body.event_data,
        )

        crated_notify = await self.repository.create_new_notification(
            self.session, notification=new_notify
        )

        if crated_notify:

            logger.info(f"Сохранён запрос на уведомление {crated_notify.id}")

            return SingleNotificationResponse(notification_id=crated_notify.id)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось сохранить уведомление",
        )

    async def update_notification_status(
        self, request_body: UpdateSendingStatusRequest
    ) -> UpdateSendingStatusResponse:
        """Обновляет в БД статус нотификации по результатам отправки"""

        updated_list = []

        logger.debug(
            f"Получено нотификаций для обновления статуса отправки:"
            f"{len(request_body.sent_success)} успешных, "
            f"{len(request_body.failure)} неудачных"
        )

        if request_body.sent_success:
            updated_sent_success = await self.repository.update_notification_status_by_id(
                session=self.session,
                notify_ids=request_body.sent_success,
                status=NotificationStatus.SENT,
            )
            if updated_sent_success:
                logger.info(
                    f"Статус: {len(updated_sent_success)} " f"успешных нотификаций обновлён"
                )
                for notify in updated_sent_success:
                    updated_list.append(str(notify.id))

        if request_body.failure:
            updated_sent_failure = await self.repository.update_notification_status_by_id(
                session=self.session,
                notify_ids=request_body.failure,
                status=NotificationStatus.SENDING_ERROR,
            )

            if updated_sent_failure:
                logger.info(
                    f"Статус: {len(updated_sent_failure)} " f"неудачных нотификаций обновлён"
                )
                for notify in updated_sent_failure:
                    updated_list.append(str(notify.id))

        return UpdateSendingStatusResponse(updated=updated_list)

    async def create_mass_notification(
        self, request_body: MassNotificationRequest
    ) -> MassNotificationResponse:
        """Создаёт массовую рассылку уведомлений всем пользователям"""

        logger.info(
            f"Получен запрос на массовую рассылку уведомлений: \
            {request_body.model_dump_json(indent=4)}"
        )

        new_mass_notification = MassNotification(
            method=request_body.method,
            source=request_body.source,
            target_start_sending_at=request_body.target_sent_at,
            priority=request_body.priority,
            event_data=request_body.event_data,
            template_id=request_body.template_id,
            event_type=request_body.event_type,
        )

        created_mass_notify = await self.repository.create_or_update_object(
            session=self.session, object=new_mass_notification
        )

        if created_mass_notify:
            logger.info(f"Созданa массовая рассылка уведомлений: {created_mass_notify.id}")
            return MassNotificationResponse(notification_id=created_mass_notify.id)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось создать массовую рассылку уведомлений",
        )


@lru_cache
def get_notification_service(
    repository: NotificationRepository = Depends(get_notification_repository),
    session: AsyncSession = Depends(get_session),
) -> NotificationService:
    return NotificationService(repository=repository, session=session)
