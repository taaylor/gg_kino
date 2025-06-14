import logging
from datetime import datetime, timezone
from typing import Any

from beanie import Document

logger = logging.getLogger(__name__)


class BaseRepository:
    collection = None

    def __init__(self, model: type[Document]):
        self.collection = model

    async def get_document(self, *filters: Any) -> Document | None:
        return await self.collection.find_one(*filters)

    async def insert_document(self, **insert_data: Any) -> Document:
        return await self.collection(**insert_data).insert()

    async def update_document(self, document: Document, **update_data: Any) -> Document:
        update_field = set(update_data.keys())
        for field in update_field:
            if hasattr(document, field):
                setattr(document, field, update_data[field])
        document.updated_at = datetime.now(timezone.utc)
        return await document.save()

    async def upsert(self, *filters: Any, **insert_data: Any) -> Document:
        # a = 1
        existing_document = await self.get_document(*filters)
        if existing_document:
            return await self.update_document(existing_document, **insert_data)
        else:
            return await self.insert_document(**insert_data)

    async def delete_document(self, *filters: Any) -> bool:
        document = await self.get_document(*filters)
        if document:
            await document.delete()
            return True
        return False
