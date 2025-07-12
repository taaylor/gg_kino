from services.repository.link_repository import LinkRepository
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    def __init__(self, repository: LinkRepository, session: AsyncSession) -> None:
        self.repository = repository
        self.session = session
