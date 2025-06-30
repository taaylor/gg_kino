from functools import lru_cache
from typing import Annotated
from uuid import UUID

from api.v1.profile.schemas import ProfileResponse
from db.cache import Cache, get_cache
from db.postgres import get_session
from fastapi import Depends
from services.profile_repository import ProfileRepository, get_profile_repository
from sqlalchemy.ext.asyncio import AsyncSession


class ProfileService:

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

    async def get_user_data_profile(self, user_id: UUID) -> ProfileResponse:

        await self.repository.fetch_user_profile_by_id(self.session_db, user_id)


@lru_cache()
def get_profile_service(
    session_db: Annotated[AsyncSession, Depends(get_session)],
    cache: Annotated[Cache, Depends(get_cache)],
    repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> ProfileService:
    return ProfileService(session_db, cache, repository)
