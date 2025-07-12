from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class EventType(StrEnum):
    TEST = "TEST"
    USER_REVIEW_LIKED = "USER_REVIEW_LIKED"
    USER_REGISTERED = "USER_REGISTERED"
    AUTO_MASS_NOTIFY = "AUTO_MASS_NOTIFY"
    MANAGER_MASS_NOTIFY = "MANAGER_MASS_NOTIFY"


class Priority(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


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


"""

{
  "event_data": {
    "recommended_films": [
      {
        "film_id": "26ee1cee-741a-417f-ad75-2890d8f69e8e",
        "film_title": "Горбатая гора",
        "imdb_rating": 10
      },
      {
        "film_id": "8bd861d1-357e-4649-8799-6915090d90db",
        "film_title": "Властелин колец",
        "imdb_rating": 9.5
      },
      {
        "film_id": "3a573f34-6071-425a-91aa-97cb229c44cf",
        "film_title": "Звёздные войны",
        "imdb_rating": 8.7
      }
    ]
  },
  "event_type": "AUTO_MASS_NOTIFY",
  "method": "EMAIL",
  "priority": "HIGH",
  "source": "event-generator",
  "template_id": "d3b2f1c4-5e6f-4c8b-9f3d-2e1f5a6b7c8d"
}
"""


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
