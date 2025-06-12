from typing import Literal

from pydantic import BaseModel, Field


class LikeRequest(BaseModel):
    rating: Literal[0, 10] = Field(
        ...,
        description="0 для дизлайка, 10 для лайка.",
    )
