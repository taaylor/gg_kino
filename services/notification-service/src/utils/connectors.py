from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
import asyncio

from core.config import app_config
from db import postgres
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from services.single_notification_processor import get_new_notification_processor


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    engine = create_async_engine(
        url=app_config.postgres.ASYNC_DATABASE_URL,
        echo=True,
        future=True,
    )
    postgres.async_session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Запускаем фоновую задачу после инициализации sessionmaker
    new_notify_processor = get_new_notification_processor()
    background_task = asyncio.create_task(new_notify_processor.process_new_notifications())

    yield

    # Отменяем фоновую задачу при завершении
    background_task.cancel()
    try:
        await background_task
    except asyncio.CancelledError:
        pass

    await engine.dispose()
