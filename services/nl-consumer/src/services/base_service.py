from services.repository.base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    def __init__(self, repository: BaseRepository, session: AsyncSession) -> None:
        self.repository = repository
        self.session = session
