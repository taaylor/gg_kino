from datetime import datetime, timezone
from uuid import UUID

from core.config import app_config
from models.enums import EventType, NotificationMethod, Priority
from pydantic import BaseModel, Field


class FilmListSchema(BaseModel):
    """Схема для ответа API, представляющая полную информацию о фильме."""

    film_id: UUID = Field(
        ...,
        description="Уникальный идентификатор фильма.",
    )
    film_title: str = Field(
        ...,
        description="Название фильма.",
    )
    imdb_rating: float | None = Field(
        None,
        description="Рейтинг фильма по версии IMDB.",
    )


class RecomendedFilmsSchema(BaseModel):
    recommended_films: list[FilmListSchema] = Field(
        default_factory=list,
        description="Список жанров фильма.",
    )


class RegularMassSendingSchemaRequest(BaseModel):
    event_data: RecomendedFilmsSchema = Field(
        ...,
        description="Данные о событиях и рекомендациях",
    )
    event_type: EventType = Field(description="Тип уведомления (например, user_review_liked)")
    method: str = Field(..., description="Тип события")
    priority: Priority = Field(description="Приоритет уведомления (например, LOW)")
    source: str = Field(..., description="Тип события")
    template_id: UUID = Field(
        ...,
        description="UUID шаблона",
    )


class ResponseToMassNotificationSchema(BaseModel):
    target_start_sending_at: datetime = Field(
        ...,
        description="Начало запуска рассылки",
    )
    event_data: RecomendedFilmsSchema = Field(
        ...,
        description="Список рекомендуемых фильмов.",
    )
    template_id: UUID = Field(
        ...,
        description="UUID шаблона для email.",
    )


class MassNotification(BaseModel):
    """Запрос на создание массовой рассылки всем пользователям"""

    event_type: EventType = EventType.MANAGER_MASS_NOTIFY
    source: str = (app_config.project_name.upper(),)
    method: NotificationMethod
    priority: Priority = Priority.HIGH
    event_data: dict = Field(default_factory=dict)
    target_sent_at: datetime | None = Field(datetime.now(timezone.utc))
    template_id: UUID
