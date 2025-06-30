from typing import Annotated

from api.v1.notification.schemas import SingleNotificationRequest, SingleNotificationResponse
from fastapi import APIRouter, Body

router = APIRouter()


@router.post(path="single-notification", response_model=SingleNotificationResponse)
async def create_single_notification(
    request_body: Annotated[SingleNotificationRequest, Body()],
) -> str:  # SingleNotificationResponse
    return "ok"
