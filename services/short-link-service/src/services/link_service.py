import logging
import secrets
import string
from functools import lru_cache
from typing import Annotated

from api.v1.link.schemas import ShortLinkRequest, ShortLinkResponse

# from core.config import app_config
from db.postgres import get_session
from fastapi import Depends
from fastapi.responses import RedirectResponse

# from models.models import ShortLink
from services.base_service import BaseService
from services.repository.link_repository import LinkRepository, get_link_repository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class LinkService(BaseService):
    """Класс реализует бизнес логику работы с короткими ссылками"""

    async def create_short_link(self, request_body: ShortLinkRequest) -> ShortLinkResponse:
        pass

    async def move_to_original(self) -> RedirectResponse:
        pass

    def _generate_path(self, length: int = 8) -> str:
        """Функция создаёт рандомную строчку для пути короткой ссылки"""
        characters = string.ascii_letters + string.digits
        return "".join(secrets.choice(characters) for _ in range(length))


@lru_cache
def get_link_service(
    repository: Annotated[LinkRepository, Depends(get_link_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LinkService:
    return LinkService(repository, session)
