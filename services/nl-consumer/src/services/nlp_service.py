import logging
from functools import lru_cache
from typing import Annotated

from api.v1.nlp.schemas import RecsRequest
from db.postgres import get_session
from fastapi import Depends
from models.logic_models import LlmResponse
from services.base_service import BaseService
from services.repository.nlp_repository import NlpRepository, get_nlp_repository
from sqlalchemy.ext.asyncio import AsyncSession
from suppliers.llm_supplier import LlmSupplier, get_llm_supplier

logger = logging.getLogger(__name__)


class NlpService(BaseService):
    def __init__(
        self, repository: NlpRepository, session: AsyncSession, llm_client: LlmSupplier
    ) -> None:
        super().__init__(repository, session)
        self.llm_client = llm_client

    async def process_nl_query(self, request_body: RecsRequest) -> LlmResponse:
        genres = {"комедия", "фантастика", "драма", "ужасы", "боевик"}  # TODO: Убрать
        return await self.llm_client.execute_nlp(genres, request_body.query)


@lru_cache()
def get_nlp_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[NlpRepository, Depends(get_nlp_repository)],
    llm_client: Annotated[LlmSupplier, Depends(get_llm_supplier)],
) -> NlpService:
    return NlpService(repository, session, llm_client)
