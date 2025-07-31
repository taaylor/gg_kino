from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class EmbeddingFields(BaseModel):
    embedding: Annotated[
        list[float], Field(..., description="Эмбеддинг рекомендаций для пользователя")
    ]
    created_at: Annotated[datetime, Field(..., description="Время создания рекомендации ")]


class UserRecsAPI(BaseModel):
    user_id: Annotated[
        UUID,
        Field(..., description="Идентификатор пользователя, для которого необходимы рекомендации"),
    ]
    embeddings: Annotated[
        list[EmbeddingFields | None],
        Field(None, description="Список рекомендаций для пользователя"),
    ]


class UserRecsRequest(BaseModel):
    user_ids: Annotated[list[UUID], Field(...)]


class UserRecsResponse(BaseModel):
    recs: Annotated[
        list[UserRecsAPI], Field(description="Рекомендации для запрошенных пользователей")
    ]
