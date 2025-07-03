import hashlib
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
    KEY_CACHE_PROFILES = "profile:users:{user_ids}"

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

    async def get_user_data_profile(self, user_id: UUID) -> ProfileResponse | None:
        key_cache = self.__class__.KEY_CACHE_PROFILE.format(user_id=user_id)

        if profile_cache := await self.cache.get(key_cache):
            logger.info(f"Найден профиль пользователя в кеше по ключу {key_cache=}")
            return ProfileResponse.model_validate_json(profile_cache)

        profile = await self.repository.fetch_user_profile_by_id(self.session_db, str(user_id))

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

    async def get_users_data_profiles(self, user_ids: list[UUID]) -> list[ProfileInternalResponse]:
        # подготавливаем ключ для кеша, используем хеш чтобы значительно сократить длину ключа
        sorted_ids = sorted(str(user_id) for user_id in user_ids)
        ids_hash = hashlib.sha256("".join(sorted_ids).encode()).hexdigest()
        key_cache = self.__class__.KEY_CACHE_PROFILES.format(user_ids=ids_hash)

        adapter = TypeAdapter(list[ProfileResponse])
        if profiles_cache := await self.cache.get(key_cache):
            logger.info(f"Найдены профили пользователей в кеше по ключу {key_cache=}")
            return adapter.validate_json(profiles_cache)

        profiles = await self.repository.fetch_list_profiles_by_ids(self.session_db, sorted_ids)

        if profiles:
            profiles_response = adapter.validate_python(profiles)
            logger.info(f"Получены профили пользователей {len(profiles_response)}")
            await self.cache.background_set(
                key=key_cache,
                value=adapter.dump_json(profiles_response),
                expire=app_config.cache_expire_in_seconds,
            )
            return profiles_response
        return []


@lru_cache()
def get_profile_service(
    session_db: Annotated[AsyncSession, Depends(get_session)],
    cache: Annotated[Cache, Depends(get_cache)],
    repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> ProfileService:
    return ProfileService(session_db, cache, repository)
