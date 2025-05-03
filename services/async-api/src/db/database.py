from abc import ABC, abstractmethod
from uuid import UUID


class BaseDB(ABC):
    """Абстрактный класс для реализации работы с хранилищем"""

    @abstractmethod
    async def get_object_by_id(self, index: str, object_id: UUID) -> dict | None:
        pass

    @abstractmethod
    async def get_list(self, query_search: dict, **kwargs) -> list:
        pass


class PaginateBaseDB(BaseDB):
    @abstractmethod
    async def get_count(self, index: str, categories: list[str], **kwargs) -> int:
        pass
