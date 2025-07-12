import logging
from typing import Annotated

from api.v1.schemes import CreateMassNotifyRequest, CreateMassNotifyResponse
from core.config import app_config
from fastapi import Depends, HTTPException, status
from models.logic_models import MassNotification
from services.connector_repository import ClientRepository, get_http_adapter

logger = logging.getLogger(__name__)


class MassNotifyService:

    def __init__(self, adapter: ClientRepository) -> None:
        self.adapter = adapter

    async def create_mass_notify(
        self, request_body: CreateMassNotifyRequest
    ) -> CreateMassNotifyResponse:
        logger.info(
            f"Получен запроса на массовую рассылку: {request_body.model_dump_json(indent=4)}"
        )

        mass_notify = MassNotification.model_validate(request_body.model_dump(mode="python"))
        logger.info(f"Собрана модель уведомления {mass_notify.model_dump_json(indent=4)}")

        response = await self.adapter.post_request(
            url=app_config.notification_api.send_to_mass_notification_url,
            json_data=mass_notify.model_dump(mode="json"),
        )

        logger.info(f"Получен ответ от сервиса нотификаций {response}")

        if response:
            return CreateMassNotifyResponse.model_validate(response)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не создать рассылку"
        )


def get_mass_notify_service(
    adapter: Annotated[ClientRepository, Depends(get_http_adapter)],
) -> MassNotifyService:
    return MassNotifyService(adapter)
