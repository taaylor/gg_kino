from typing import Annotated

from fastapi import APIRouter, Depends, Path
from fastapi.responses import RedirectResponse
from services.link_service import LinkService, get_link_service

router = APIRouter()


@router.get(path="/{short_link_code}")
async def move_to_original(
    service: Annotated[LinkService, Depends(get_link_service)],
    path: Annotated[str, Path(alias="short_link_code")],
) -> RedirectResponse:
    return await service.move_to_original(path)
