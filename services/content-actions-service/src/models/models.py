from datetime import datetime, timezone
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field


class LikeCollection(Document):
    id: UUID = Field(default_factory=uuid4)
    text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
