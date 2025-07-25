from models.models import ProcessedNpl
from services.repository.base_repository import BaseRepository


class NlpRepository(BaseRepository[ProcessedNpl]):
    """Репозиторий для работы с экземплярами npl в базе данных."""


def get_nlp_repository() -> NlpRepository:
    """Возвращает экземпляр репозитория для работы с npl."""
    return NlpRepository(ProcessedNpl)
