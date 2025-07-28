from models.models import UserRecs
from services.repository.base_repository import BaseRepository


class RecsRepository(BaseRepository[UserRecs]):
    """Репозиторий для работы с экземплярами npl в базе данных."""


def get_recs_repository() -> RecsRepository:
    """Возвращает экземпляр репозитория для работы с npl."""
    return RecsRepository(UserRecs)
