from contextlib import asynccontextmanager

from beanie import init_beanie
from core.config import app_config
from fastapi import FastAPI
from models.models import Bookmark, Rating, Review
from motor.motor_asyncio import AsyncIOMotorClient


@asynccontextmanager
async def lifespan(app: FastAPI):

    engine = AsyncIOMotorClient(app_config.mongodb.ASYNC_DATABASE_URL)
    await init_beanie(
        database=engine[app_config.mongodb.name],
        document_models=[
            Rating,
            Review,
            Bookmark,
        ],
    )

    yield

    engine.close()
