import datetime
import logging
import uuid

from api.v1.auth.schemas import Session
from core.config import app_config
from fastapi import Depends
from models.logic_models import SessionUserData
from models.models import UserSession, UserSessionsHist
from utils.key_manager import JWTProcessor, get_key_manager

logger = logging.getLogger(__name__)


class SessionMaker:
    def __init__(self, key_manager: JWTProcessor):
        self.key_manager = key_manager

    async def create_session(
        self, user_data: SessionUserData
    ) -> tuple[Session, UserSession, UserSessionsHist]:
        user_data.session_id = uuid.uuid4()

        access_token, refresh_token = await self._create_tokens(user_data=user_data)

        user_session = UserSession(
            session_id=user_data.session_id,
            user_id=user_data.user_id,
            user_agent=user_data.user_agent,
            refresh_token=refresh_token,
            expires_at=datetime.datetime.now()
            + datetime.timedelta(seconds=app_config.jwt.refresh_token_lifetime_sec),
        )

        user_session_hist = UserSessionsHist(
            session_id=user_session.session_id,
            user_id=user_session.user_id,
            user_agent=user_session.user_agent,
            expires_at=user_session.expires_at,
        )

        user_tokens = Session(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=user_session.expires_at,
        )

        return user_tokens, user_session, user_session_hist

    async def update_session(self, user_data: SessionUserData) -> tuple[Session, UserSession]:
        access_token, refresh_token = await self._create_tokens(user_data=user_data)

        user_session = UserSession(
            session_id=user_data.session_id,
            user_id=user_data.user_id,
            user_agent=user_data.user_agent,
            refresh_token=refresh_token,
            expires_at=datetime.datetime.now()
            + datetime.timedelta(seconds=app_config.jwt.refresh_token_lifetime_sec),
        )

        user_tokens = Session(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=user_session.expires_at,
        )

        return user_tokens, user_session

    async def _create_tokens(self, user_data: SessionUserData):
        access_token, refresh_token = await self.key_manager.create_tokens(user_data=user_data)
        return access_token, refresh_token


def get_auth_session_maker(key_manager: JWTProcessor = (Depends(get_key_manager))):
    return SessionMaker(key_manager=key_manager)
