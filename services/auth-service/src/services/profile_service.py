import logging
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from api.v1.internal.schemes import ProfileInternalResponse
from api.v1.profile.schemas import ProfileResponse
from core.config import app_config
from db.cache import Cache, get_cache
from db.postgres import get_session
from fastapi import Depends
from pydantic import TypeAdapter
from services.profile_repository import ProfileRepository, get_profile_repository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ProfileService:
    KEY_CACHE_PROFILE = "profile:user:{user_id}"

    __slots__ = ("session_db", "cache", "repository")

    def __init__(
        self,
        session_db: AsyncSession,
        cache: Cache,
        repository: ProfileRepository,
    ):
        self.session_db = session_db
        self.cache = cache
        self.repository = repository

    async def fetch_user_profile(self, user_id: UUID) -> ProfileResponse | None:
        key_cache = self.__class__.KEY_CACHE_PROFILE.format(user_id=user_id)

        if profile_cache := await self.cache.get(key_cache):
            logger.info(f"Найден профиль пользователя в кеше по ключу {key_cache=}")
            return ProfileResponse.model_validate_json(profile_cache)

        profile = await self.repository.fetch_user_profile_by_id(self.session_db, user_id)

        if profile:
            profile_response = ProfileResponse(**profile)
            logger.info(f"Получен профиль пользователя {user_id=}")
            await self.cache.background_set(
                key=key_cache,
                value=profile_response.model_dump_json(),
                expire=app_config.cache_expire_in_seconds,
            )
            return profile_response
        return None

    async def fetch_users_profiles_list(
        self, user_ids: list[UUID]
    ) -> list[ProfileInternalResponse]:
        adapter = TypeAdapter(list[ProfileResponse])
        profiles = await self.repository.fetch_list_profiles_by_ids(self.session_db, user_ids)

        if not profiles:
            logger.info("Не найдено профилей для запрошенных user_ids")
            return []

        logger.info(f"Получены профили {len(profiles)} пользователей")
        profiles_response = adapter.validate_python(profiles)
        return profiles_response


@lru_cache()
def get_profile_service(
    session_db: Annotated[AsyncSession, Depends(get_session)],
    cache: Annotated[Cache, Depends(get_cache)],
    repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> ProfileService:
    return ProfileService(session_db, cache, repository)
