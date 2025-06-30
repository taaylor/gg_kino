import logging
from functools import lru_cache
from typing import Any

from models.models import User, UserCred, UserProfileSettings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.decorators import sqlalchemy_universal_decorator

logger = logging.getLogger(__name__)


class ProfileRepository:

    __slots__ = ()

    @sqlalchemy_universal_decorator
    async def fetch_user_profile_by_id(
        self, session: AsyncSession, user_id: str
    ) -> dict[str, Any] | None:
        stmt = (
            select(
                User.id.label("user_id"),
                User.username,
                User.first_name,
                User.last_name,
                User.gender,
                User.role_code.label("role"),
                User.created_at.label("date_create_account"),
                UserCred.email,
                UserCred.is_fictional_email,
                UserCred.is_verification_email,
                UserProfileSettings.user_timezone,
                UserProfileSettings.is_notification_email,
            )
            .join(UserCred, User.id == UserCred.user_id)
            .join(UserProfileSettings, User.id == UserProfileSettings.user_id)
            .where(User.id == user_id)
        )

        result = (await session.execute(stmt)).one_or_none()

        if not result:
            return None
        return dict(result._mapping)


@lru_cache
def get_profile_repository() -> ProfileRepository:
    return ProfileRepository()
