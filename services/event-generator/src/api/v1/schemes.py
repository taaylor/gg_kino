import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import lxml
import lxml.html
from fastapi import HTTPException, status
from jinja2 import Template as JinjaTemplate
from jinja2 import TemplateSyntaxError
from models.enums import NotificationMethod, Priority
from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)


class TemplateBase(BaseModel):
    name: str = Field(..., description="Наименование шаблона")
    description: str = Field(..., description="Описание шаблона")
    template_type: str = Field(..., description="Тип шаблона (например, email, sms и т.д.)")
    content: str = Field(..., description="HTML код шаблона")

    model_config = ConfigDict(from_attributes=True)


class TemplateRequest(TemplateBase):

    @field_validator("content")
    @classmethod
    def validator_content(cls, content: Any):
        try:
            JinjaTemplate(content)
            tree = lxml.html.fromstring(content)
            if tree.xpath("//script"):
                logger.warning("Шаблон содержит запрещённые <script> теги")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Шаблон содержит запрещённые <script> теги",
                )
            return content
        except TemplateSyntaxError as error:
            logger.warning(f"Некорректный синтакс шаблона Jinja {error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Некорректный синтакс шаблона Jinja"
            )
        except Exception as error:
            logger.warning(f"Некорректный синтакс шаблона {error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Некорректный синтакс шаблона"
            )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Шаблон регистрации пользователя",
                    "description": "Шаблон письма с благодарностью за регистрацию пользователя",
                    "template_type": "email",
                    "content": "<html><body><h1>Спасибо за регистрацию, {{ username }}!</h1><p>Мы "
                    "рады видеть вас среди наших пользователей.</p></body></html>",
                }
            ]
        }
    }


class TemplateResponse(TemplateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime = Field(exclude=True)


class GetAllTemplatesResponse(BaseModel):
    templates: list[TemplateResponse] = Field(..., description="Список всех шаблонов")


class CreateMassNotifyRequest(BaseModel):
    """Запрос на создание массовой рассылки всем пользователям"""

    method: NotificationMethod = Field(..., description="Канал для уведомления пользователя")
    priority: Priority = Field(
        Priority.HIGH,
        description="Приоритет, с которым будет отправлено уведомление. HIGH доставляются без учёта таймзоны пользователя",  # noqa: E501
    )
    event_data: dict = Field(
        default_factory=dict,
        description="Контекст события, которое привело к запросу на нотификацию",
    )
    target_sent_at: datetime | None = Field(
        datetime.now(timezone.utc), description="Желаемое время отправки уведомления"
    )
    template_id: UUID | None = Field(
        default=None,
        description="Идентификатор шаблона, который будет использоваться для массовой рассылки",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "method": "EMAIL",
                    "priority": "HIGH",
                    "target_sent_at": "2025-07-12T17:48:17.762107Z",
                    "template_id": "f69248f5-4f6c-4cd4-82ca-e8f6cd68483f",
                }
            ]
        }
    }


class CreateMassNotifyResponse(BaseModel):
    """Ответ о создании массовой рассылки"""

    notification_id: UUID = Field(
        ..., description="Уникальный идентификатор экземпляра уведомления"
    )
