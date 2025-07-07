from typing import Annotated

from api.v1.notification.schemas import (
    SingleNotificationRequest,
    SingleNotificationResponse,
    UpdateSendingStatusRequest,
    UpdateSendingStatusResponse,
)
from fastapi import APIRouter, Body, Depends
from services.notification_service import NotificationService, get_notification_service

router = APIRouter()


@router.post(
    path="/single-notification",
    response_model=SingleNotificationResponse,
    summary="Создание единичного уведомления",
    description="Этот эндпоинт позволяет создать и отправить одиночное уведомление.",
)
async def create_single_notification(
    service: Annotated[NotificationService, Depends(get_notification_service)],
    request_body: Annotated[SingleNotificationRequest, Body()],
) -> SingleNotificationResponse:
    return await service.send_single_notification(request_body=request_body)


@router.post(
    path="/update-sending-status",
    response_model=UpdateSendingStatusResponse,
    summary="Обновление статуса отправки уведомления",
    description="Этот эндпоинт обновляет статус отправки уведомления.",
)
async def update_sending_status(
    service: Annotated[NotificationService, Depends(get_notification_service)],
    request_body: Annotated[UpdateSendingStatusRequest, Body()],
) -> UpdateSendingStatusResponse:
    return await service.update_notification_status(request_body=request_body)
