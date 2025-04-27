from uuid import UUID

from pydantic import BaseModel, Field


class PersonInFilmsResponse(BaseModel):
    """
    Схема для ответа API, представляющая информацию о фильме, в котором участвует персона.
    """

    uuid: UUID = Field(
        ...,  # обязательное поле
        description="Уникальный идентификатор фильма.",
    )
    roles: list[str] = Field(
        ...,  # обязательное поле
        description=("Список ролей персоны в фильме (например, 'actor', 'director', 'writer')."),
    )


class PersonResponse(BaseModel):
    """
    Модель для ответа API, представляющая человека (актера, сценариста, режиссера).
    """

    uuid: UUID = Field(
        ...,
        description="Уникальный идентификатор персоны.",
    )
    full_name: str = Field(
        ...,
        description="Полное имя персоны.",
    )
    films: list[PersonInFilmsResponse] | None = Field(
        None,
        description="Список фильмов, в которых участвовала персона.",
    )
