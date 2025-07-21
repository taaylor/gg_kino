from services.repository.base_repository import BaseRepository


class NlpRepository(BaseRepository):
    """Репозиторий для работы с экземплярами npl в БД"""


def get_nlp_repository() -> NlpRepository:
    return NlpRepository()
