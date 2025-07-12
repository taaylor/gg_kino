from typing import Annotated

from api.v1.schemes import CreateMassNotifyRequest, CreateMassNotifyResponse
from fastapi import APIRouter, Body, Depends
from services.mass_notify_service import MassNotifyService, get_mass_notify_service

router = APIRouter()


@router.post(
    path="/create-mass-notify",
    response_model=CreateMassNotifyResponse,
    summary="Создать массовую рассылку",
    description="Метод запускает массовую рассылку по заданному шаблону",
)
async def create_mass_notify(
    service: Annotated[MassNotifyService, Depends(get_mass_notify_service)],
    request_body: Annotated[CreateMassNotifyRequest, Body()],
) -> CreateMassNotifyResponse:
    return await service.create_mass_notify(request_body)
