from pydantic import BaseModel, Field


class ObjectModel(BaseModel):

    id: str
    text: str = Field(max_length=999)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "1234",
                    "text": "Star Wars: Episode IV - A New Hope. Sci‑Fi, Action, Adventure. "
                    "high rating. The Imperial Forces, under orders from cruel Darth Vader, "
                    "hold Princess Leia hostage in their efforts to quell the rebellion against "
                    "Galactic Empire. Luke Skywalker and Han Solo, of the Millennium Falcon, "
                    "work together with the companionable droid duo R2‑D2 and C‑3PO to rescue the "
                    "beautiful princess, help the Rebel Alliance and restore freedom and "
                    "justice to the Galaxy.",
                }
            ]
        }
    }


class EmbeddingRequest(BaseModel):
    objects: list[ObjectModel] = Field(min_length=1, max_length=100)


class EmbeddingResponse(BaseModel):
    id: str
    embedding: str
