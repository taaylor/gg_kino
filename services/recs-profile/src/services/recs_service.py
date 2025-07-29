import logging
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from api.v1.recs_profile.schemas import (
    EmbeddingFields,
    UserRecsAPI,
    UserRecsRequest,
    UserRecsResponse,
)
from db.postgres import get_session
from fastapi import Depends
from models.models import UserRecs
from services.base_service import BaseService
from services.repository.recs_repository import RecsRepository, get_recs_repository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class RecsService(BaseService[RecsRepository]):
    """Класс реализует бизнес логику поиска эмбеддингов в БД для списка пользователей"""

    async def fetch_user_recs(self, request_body: UserRecsRequest) -> UserRecsResponse:
        """Возвращает рекомендации для списка пользователей."""

        recs_for_users = await self._fetch_from_repository(request_body.user_ids)
        if not recs_for_users:
            return UserRecsResponse(
                recs=[UserRecsAPI(user_id=user, embeddings=[]) for user in request_body.user_ids]
            )

        # Формирую ответ для каждого запрошенного пользователя
        user_recs_list = []
        for user_id in request_body.user_ids:
            user_recs = recs_for_users.get(user_id, [])

            # Преобразую объекты UserRecs в EmbeddingFields
            embeddings = []
            for rec in user_recs:
                if rec.embedding:
                    embeddings.append(
                        EmbeddingFields(embedding=rec.embedding, created_at=rec.created_at)
                    )

            user_recs_list.append(UserRecsAPI(user_id=user_id, embeddings=embeddings))

        return UserRecsResponse(recs=user_recs_list)

    async def _fetch_from_repository(
        self, user_ids: list[UUID]
    ) -> dict[UUID, list[UserRecs]] | None:
        """Извлекает рекомендации из репозитория и группирует их по user_id."""

        recs = await self.repository.fetch_recs_from_db(self.session, user_ids)
        logger.info(f"Получены рекомендации из БД: {len(recs) if recs else 0}")

        if not recs:
            return None

        # Группирую рекомендации по user_id
        recs_for_users = {}
        for rec in recs:
            if rec.user_id not in recs_for_users:
                recs_for_users[rec.user_id] = []
            recs_for_users[rec.user_id].append(rec)
        return recs_for_users


@lru_cache()
def get_recs_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[RecsRepository, Depends(get_recs_repository)],
) -> RecsService:
    return RecsService(repository, session)
