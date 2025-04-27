from uuid import UUID

from pydantic import BaseModel, Field


class GenreResponse(BaseModel):
    """
    Схема для ответа API, представляющая информацию о жанре фильма.
    """

    uuid: UUID = Field(..., description="Уникальный идентификатор жанра.")
    name: str = Field(..., description="Название жанра фильма.")
