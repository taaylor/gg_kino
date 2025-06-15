import logging
from uuid import UUID

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    path="/{film_id}/bookmark-test",
)
async def test_endpoint_bookmark(
    film_id: UUID,
):
    return {
        "status": "ok",
    }
