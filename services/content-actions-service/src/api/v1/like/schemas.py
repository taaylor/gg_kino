from uuid import UUID

from pydantic import BaseModel


class LikeRequest(BaseModel):
    film_id: UUID
