from datetime import datetime
from typing import Annotated
from uuid import UUID

from core.config import app_config
from pydantic import AnyHttpUrl, BaseModel, BeforeValidator, Field


def validate_url(url: str) -> AnyHttpUrl:
    return AnyHttpUrl(url)


class ShortLinkRequest(BaseModel):
    url: Annotated[
        AnyHttpUrl,
        BeforeValidator(validate_url),
        Field(
            ...,
            description="Полная ссылка, которую необходимо сократить.",
            examples=["https://spastv.ru/"],
        ),
    ]
    valid_days: Annotated[
        int,
        Field(
            app_config.shortlink.link_lifetime_days,
            description="Количество дней, которые должна действовать ссылка",
        ),
    ]


class ShortLinkResponse(BaseModel):
    id: UUID = Field(..., description="Уникальный идентификатор сокращённой ссылки")
    short_url: Annotated[
        AnyHttpUrl,
        BeforeValidator(validate_url),
        Field(
            ...,
            description="Сокращённая ссылка",
            examples=["http://link.ru/dxaNwHV0"],
        ),
    ]
    original_url: Annotated[
        AnyHttpUrl,
        BeforeValidator(validate_url),
        Field(
            ...,
            description="Полная ссылка ссылка",
            examples=["http://link.ru/dxaNwHV0"],
        ),
    ]
    valid_to: Annotated[
        datetime, Field(..., description="Время, до которого сокращённая ссылка будет действовать.")
    ]
