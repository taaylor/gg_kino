import base64
import logging
from functools import lru_cache
from typing import Annotated

import numpy as np
from api.v1.schemas import EmbeddingRequest, EmbeddingResponse
from fastapi import Depends
from sentence_transformers import SentenceTransformer
from services.ai_model import get_ai_model

logger = logging.getLogger(__name__)


class EmbeddingService:

    __slots__ = ("ai_model",)

    def __init__(self, ai_model: SentenceTransformer):
        self.ai_model = ai_model

    def fetch_embeddings_objects(self, objects: EmbeddingRequest) -> list[EmbeddingResponse]:
        list_objects = objects.objects
        embeddings_obj = []
        for object in list_objects:
            embedding = self.ai_model.encode(object.text, convert_to_tensor=False)
            logger.info(f"Для объекта с идентификатором {object.id} сформирован {embedding=}")
            logger.info(f"Размерность: {len(embedding)}")
            embedding_base64 = base64.b64encode(embedding.astype(np.float32).tobytes()).decode(
                "utf-8"
            )
            embeddings_obj.append(EmbeddingResponse(id=object.id, embedding=embedding_base64))
        return embeddings_obj


@lru_cache()
def get_embedding_service(
    ai_model: Annotated[SentenceTransformer, Depends(get_ai_model)],
) -> EmbeddingService:
    return EmbeddingService(ai_model=ai_model)
