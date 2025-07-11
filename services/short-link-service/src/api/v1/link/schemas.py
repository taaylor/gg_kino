from datetime import datetime
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, Field


class ShortLinkRequest(BaseModel):
    url: AnyHttpUrl = Field(
        ...,
        description="Полная ссылка, которую необходимо сократить.",
        examples=["https://spastv.ru/"],
    )


class ShortLinkResponse(BaseModel):
    link_id: UUID = Field(..., description="Уникальный идентификатор сокращённой ссылки")
    url: AnyHttpUrl = Field(
        ...,
        description="Сокращённая ссылка",
        examples=["http://link.ru/1"],
    )
    valid_to: datetime = Field(
        ..., description="Время, до которого сокращённая ссылка будет действовать."
    )
