import logging
from functools import lru_cache
from typing import Any

from models.models import User, UserCred, UserProfileSettings
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.decorators import sqlalchemy_universal_decorator

logger = logging.getLogger(__name__)


class ProfileRepository:

    __slots__ = ()

    @staticmethod
    def _base_profile_query() -> Select:
        """Базовый запрос для получения профиля с основными полями"""
        return (
            select(
                User.id.label("user_id"),
                User.username,
                User.first_name,
                User.last_name,
                User.gender,
                User.role_code.label("role"),
                User.created_at,
                UserCred.email,
                UserCred.is_fictional_email,
                UserCred.is_verified_email,
                UserProfileSettings.user_timezone,
                UserProfileSettings.is_email_notify_allowed,
            )
            .join(UserCred, User.id == UserCred.user_id)
            .join(UserProfileSettings, User.id == UserProfileSettings.user_id)
        )

    @sqlalchemy_universal_decorator
    async def fetch_user_profile_by_id(
        self, session: AsyncSession, user_id: str
    ) -> dict[str, Any] | None:
        stmt = self._base_profile_query().where(User.id == user_id)
        result = (await session.execute(stmt)).one_or_none()

        if not result:
            return None

        return dict(result._mapping)

    @sqlalchemy_universal_decorator
    async def fetch_list_profiles_by_ids(
        self, session: AsyncSession, user_ids: list[str]
    ) -> list[dict[str, Any]]:
        stmt = self._base_profile_query().where(User.id.in_(user_ids))
        result = (await session.execute(stmt)).all()
        return [dict(profile._mapping) for profile in result]


@lru_cache
def get_profile_repository() -> ProfileRepository:
    return ProfileRepository()
