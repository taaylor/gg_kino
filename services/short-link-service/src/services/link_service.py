import logging
import secrets
import string
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Annotated
from zoneinfo import ZoneInfo

from api.v1.link.schemas import ShortLinkRequest, ShortLinkResponse
from core.config import app_config
from db.postgres import get_session
from fastapi import Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from models.models import ShortLink
from services.base_service import BaseService
from services.repository.link_repository import LinkRepository, get_link_repository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class LinkService(BaseService):
    """Класс реализует бизнес логику работы с короткими ссылками"""

    async def create_short_link(self, request_body: ShortLinkRequest) -> ShortLinkResponse:
        """Функция создаёт короткую ссылку и записывает её в БД"""

        logger.info(f"Получен запрос на сокращение ссылки: {request_body.url}")

        # Создаём новый path для короткой ссылки и проверяем, что такого ещё нет в БД
        new_path = self._generate_path()
        logger.info(f"Создан path для короткой ссылки: {new_path}")

        while await self.repository.check_path(self.session, new_path):
            new_path = self._generate_path()
            logger.info(f"Path оказался дублированным созданы новый: {new_path}")

        # Подготавливаем данные для записи новый ссылки в БД
        short_url = app_config.shortlink.get_short_url + new_path
        logger.info(f"Создана короткая ссылка: {short_url}. Для длинной {request_body.url}.")
        valid_to = datetime.now(ZoneInfo("UTC")) + timedelta(days=request_body.valid_days)

        new_link = ShortLink(
            original_url=str(request_body.url),
            short_url=short_url,
            short_path=new_path,
            valid_to=valid_to,
        )

        created_link = await self.repository.create_object(self.session, new_link)

        if created_link:
            response = ShortLinkResponse(
                id=created_link.id,
                short_url=created_link.short_url,  # type: ignore
                original_url=created_link.original_url,  # type: ignore
                valid_to=created_link.valid_to,
            )

            logger.info(
                f"Ссылка: {request_body.url} сокращена: {response.model_dump_json(indent=4)}"
            )

            return response

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось выполнить сокращение из-за внутренней ошибки",
        )

    async def move_to_original(self, path: str) -> RedirectResponse:
        """Функция находит оригинальную ссылку для сокращённой и производит роутинг"""

        logger.info(f"Получен запрос на редирект по ссылке с path: {path}")

        link = await self.repository.fetch_original_by_short(self.session, path)

        if not link:
            logger.warning(f"Для {path=} не найдена оригинальная ссылка")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для короткой ссылки не найдена оригинальная",
            )
        elif link.valid_to < datetime.now(ZoneInfo("UTC")):
            logger.warning(f"Для {path=} редирект устарел: {link.valid_to}")
            # Если пользователь перешёл по устаревшей ссылке, то помечаю её архивной
            link.is_archive = True
            await self.repository.update_object(self.session, link)

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Время жизни короткой ссылки истекло",
            )
        logger.info(f"Для {path=} найдена оригинальная ссылка: {link.original_url}")
        return RedirectResponse(link.original_url)

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
