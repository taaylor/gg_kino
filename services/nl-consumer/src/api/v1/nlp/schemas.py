from typing import Annotated

from pydantic import BaseModel, Field


class RecsRequest(BaseModel):
    query: Annotated[
        str,
        Field(
            ..., min_length=10, max_length=500, description="Пользовательский запрос рекомендации"
        ),
    ]
