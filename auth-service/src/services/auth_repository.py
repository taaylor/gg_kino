import logging

from models.models import DictRoles, RolesPermissions, User, UserCred, UserSession, UserSessionsHist
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.decorators import sqlalchemy_handler_exeptions

logger = logging.getLogger(__name__)


class AuthReository:
    @sqlalchemy_handler_exeptions
    async def fetch_user_by_name(self, session: AsyncSession, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @sqlalchemy_handler_exeptions
    async def fetch_user_by_email(self, session: AsyncSession, email: str) -> User | None:
        stmt = select(User).join(UserCred).where(UserCred.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @sqlalchemy_handler_exeptions
    async def fetch_usercred_by_email(self, session: AsyncSession, email: str) -> UserCred | None:
        stmt = select(UserCred).where(UserCred.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @sqlalchemy_handler_exeptions
    async def fetch_permissions_for_role(self, session: AsyncSession, role_code: str) -> list[str]:
        stmt = (
            select(RolesPermissions.permission).join(DictRoles).where(DictRoles.role == role_code)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @sqlalchemy_handler_exeptions
    async def create_user_in_repository(
        self,
        session: AsyncSession,
        user: User,
        user_cred: UserCred,
        user_session: UserSession,
        user_session_hist: UserSessionsHist,
    ):
        session.add_all([user, user_cred, user_session, user_session_hist])

    @sqlalchemy_handler_exeptions
    async def create_session_in_repository(
        self,
        session: AsyncSession,
        user_session: UserSession,
        user_session_hist: UserSessionsHist,
    ):
        session.add_all([user_session, user_session_hist])


def get_auth_repository():
    return AuthReository()
