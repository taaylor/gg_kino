from services.repository.base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService[TRepository: BaseRepository]:
    def __init__(self, repository: TRepository, session: AsyncSession) -> None:
        self.repository: TRepository = repository
        self.session = session
