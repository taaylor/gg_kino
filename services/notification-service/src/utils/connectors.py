from contextlib import asynccontextmanager

from core.config import app_config
from db import postgres
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_async_engine(
        app_config.postgres.ASYNC_DATABASE_URL,
        echo=True,
        future=True,
    )
    postgres.async_session_maker = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    yield

    await engine.dispose()
