import logging
from datetime import datetime, timezone

# from functools import lru_cache

# from beanie import Document

# from api.v1.like.schemas import OutputRating
# from fastapi import HTTPException, status
# from models.models import Like


logger = logging.getLogger(__name__)


class BaseRepository:
    collection = None

    @classmethod
    async def get_document(cls, *filters):
        return await cls.collection.find_one(*filters)

    @classmethod
    async def insert_document(cls, **insert_data):
        return await cls.collection(**insert_data).insert()

    @classmethod
    async def update_document(cls, document, update_field: list, **update_data):
        for field in update_field:
            if hasattr(document, field):
                setattr(document, field, update_data[field])
        document.updated_at = datetime.now(timezone.utc)
        return await document.save()

    @classmethod
    async def upsert(cls, *filters, update_fields: list, **insert_data):
        # a = 1
        existing_document = await cls.get_document(*filters)
        if existing_document:
            return await cls.update_document(existing_document, update_fields, **insert_data)
        else:
            return await cls.insert_document(**insert_data)

    @classmethod
    async def delete_document(cls, *filters):
        document = await cls.get_document(*filters)
        if document:
            await document.delete()
            return True
        return False
