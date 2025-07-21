from typing import Annotated

from api.v1.nlp.schemas import RecsRequest
from auth_utils import LibAuthJWT, auth_dep
from fastapi import APIRouter, Body, Depends
from models.logic_models import LlmResponse
from services.nlp_service import NlpService, get_nlp_service

# from uuid import UUID


router = APIRouter()


@router.post("/analyze")
async def process_query(
    authorize: Annotated[LibAuthJWT, Depends(auth_dep)],
    service: Annotated[NlpService, Depends(get_nlp_service)],
    request_body: Annotated[RecsRequest, Body],
) -> LlmResponse:
    # await authorize.jwt_required()
    # user_jwt_id = UUID((await authorize.get_raw_jwt()).get("user_id"))
    return await service.process_nl_query(request_body)
