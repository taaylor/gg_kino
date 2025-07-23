from contextlib import asynccontextmanager

from fastapi import FastAPI
from services.ai_model import get_ai_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging

    logger = logging.getLogger(__name__)

    get_ai_model()
    logger.info("AI модель успешно интегрирована")
    yield
