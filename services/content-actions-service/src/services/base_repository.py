import logging
from datetime import datetime, timezone
from typing import Any

from beanie import Document

logger = logging.getLogger(__name__)


class BaseRepository:
    """Базовый репозиторий для CRUD работы с Beanie Document-моделями."""

    __slots__ = [
        "collection",
    ]

    def __init__(self, model: type[Document]):
        """
        Инициализирует репозиторий с указанной Beanie-моделью.

        :param model: Класс модели, наследник beanie.Document.
        """

        self.collection = model

    async def get_document(self, *filters: Any) -> Document | None:
        """
        Находит один документ по переданным фильтрам.

        :param filters: Условия поиска, например Model.user_id == user_id, Model.film_id == film_id
        :return: Экземпляр модели Document или None, если не найден.
        """
        logger.debug(f"Поиск документа по фильтрам {filters}.")
        return await self.collection.find_one(*filters)

    async def insert_document(self, **insert_data: Any) -> Document:
        """
        Создаёт новый документ.

        :param insert_data: Поля для создания документа,
                            например user_id=user_id, film_id=film_id, score=score.
        :return: Вставленный экземпляр модели Document.
        """

        logger.debug(f"Создание документа с данными {insert_data}.")
        return await self.collection(**insert_data).insert()

    async def update_document(self, document: Document, **update_data: Any) -> Document:
        """
        Обновляет поля в переданном экземпляре документа и сохраняет.

        :param document: Ранее полученный экземпляр модели.
        :param update_data: Поля и новые значения для обновления, например score=new_score.
        :return: Обновлённый экземпляр модели Document.
        """

        logger.debug(f"Обновление документа с данными {update_data}.")
        update_field = set(update_data.keys())
        for field in update_field:
            if hasattr(document, field):
                setattr(document, field, update_data[field])
        document.updated_at = datetime.now(timezone.utc)
        return await document.save()

    async def upsert(self, *filters: Any, **insert_data: Any) -> Document:
        """
        Если документ по фильтрам найден — обновляет его полями из insert_data,
        иначе — создаёт новый документ с переданными данными.

        :param filters: Условия поиска для существующего документа,
                        например Model.user_id == user_id.
        :param insert_data: Поля для вставки или обновления,
                            например user_id=user_id, film_id=film_id, score=score.
        :return: Экземпляр модели Document после операции.
        """

        existing_document = await self.get_document(*filters)
        logger.debug(
            "Обновление/создание документа.\n"
            f" Поиск по фильтрам {filters}.\n"
            f" Создание/обновление документа с данными {insert_data}."
        )
        if existing_document:
            return await self.update_document(existing_document, **insert_data)
        else:
            return await self.insert_document(**insert_data)

    async def delete_document(self, *filters: Any) -> bool:
        """
        Удаляет один документ по переданным фильтрам.

        :param filters: Условия поиска для удаления,
                        например Model.user_id == user_id, Model.film_id == film_id.
        :return: True, если документ найден и удалён; False, если не найден.
        """

        existing_document = await self.get_document(*filters)
        if existing_document:
            await existing_document.delete()
            logger.debug(f"Документ по фильтрам {filters} найден и удалён.")
            return True
        logger.debug(f"Документ по фильтрам {filters} не найден и не может быть удалён.")
        return False
