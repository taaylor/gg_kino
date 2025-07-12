from typing import Annotated

from api.v1.link.schemas import ShortLinkRequest, ShortLinkResponse
from fastapi import APIRouter, Body, Depends
from services.link_service import LinkService, get_link_service

router = APIRouter()


@router.post(
    path="/shorten",
    response_model=ShortLinkResponse,
    summary="Сократить ссылку",
    description="""Этот запрос принимает полную ссылку, а возвращает
    сокращённую, при переходе по которой будет редерект на полную""",
)
async def create_short_link(
    service: Annotated[LinkService, Depends(get_link_service)],
    request_body: Annotated[ShortLinkRequest, Body()],
) -> ShortLinkResponse:
    return await service.create_short_link(request_body)
