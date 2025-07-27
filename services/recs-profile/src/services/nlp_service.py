import logging
from functools import lru_cache
from typing import Annotated

# from api.v1.recs_profile.schemas import UserRecsRequest, UserRecsResponse
from db.postgres import get_session
from fastapi import Depends

# from models.enums import ProcessingStatus
# from models.logic_models import FilmListResponse
# from models.models import ProcessedNpl
from services.base_service import BaseService
from services.repository.nlp_repository import NlpRepository, get_nlp_repository
from sqlalchemy.ext.asyncio import AsyncSession
from suppliers.embedding_supplier import EmbeddingSupplier, get_embedding_supplier
from suppliers.film_supplier import FilmSupplier, get_film_supplier

logger = logging.getLogger(__name__)


class NlpService(BaseService):
    def __init__(
        self,
        repository: NlpRepository,
        session: AsyncSession,
        film_supplier: FilmSupplier,
        embedding_supplier: EmbeddingSupplier,
    ) -> None:
        super().__init__(repository, session)
        self.film_supplier = film_supplier
        self.embedding_supplier = embedding_supplier


@lru_cache()
def get_nlp_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[NlpRepository, Depends(get_nlp_repository)],
    film_supplier: Annotated[FilmSupplier, Depends(get_film_supplier)],
    embedding_supplier: Annotated[EmbeddingSupplier, Depends(get_embedding_supplier)],
) -> NlpService:
    return NlpService(repository, session, film_supplier, embedding_supplier)
