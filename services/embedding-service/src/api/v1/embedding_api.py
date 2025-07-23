from typing import Annotated

from api.v1.schemas import EmbeddingRequest, EmbeddingResponse
from core.config import app_config
from fastapi import APIRouter, Body, Depends
from services.embedding_service import EmbeddingService, get_embedding_service

router = APIRouter()


@router.post(
    path="/fetch-embeddings",
    summary="Получение векторных представлений (эмбеддингов) для текстов",
    description=(
        "Эндпоинт принимает список текстов на любом языке (например, русском или английском) "
        "и возвращает их векторные представления (эмбеддинги), сгенерированные с помощью модели "
        "`paraphrase-multilingual-MiniLM-L12-v2`. Эти векторы могут быть использованы для задач "
        "поиска, классификации или построения рекомендательных систем, например, в Elasticsearch. "
        f"Каждый вектор имеет размерность {app_config.ai_model.truncate_dim} "
        "(усеченная для оптимизации производительности). "
        "Модель поддерживает кросс-языковые запросы, что позволяет сопоставлять тексты на "
        "разных языках."
    ),
    response_model=list[EmbeddingResponse],
)
def fetch_embeddings(
    request_model: Annotated[EmbeddingRequest, Body()],
    service: Annotated[EmbeddingService, Depends(get_embedding_service)],
) -> list[EmbeddingResponse]:
    return service.fetch_embeddings_objects(request_model)
