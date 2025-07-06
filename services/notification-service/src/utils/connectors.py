import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from core.config import app_config
from db import postgres, rabbitmq
from fastapi import FastAPI
from services.processors.single_notification_processor import get_new_notification_processor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    engine = create_async_engine(
        url=app_config.postgres.ASYNC_DATABASE_URL,
        echo=False,
        future=True,
    )
    postgres.async_session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Создаём сессию к RabbitMQ сначала
    await rabbitmq.get_producer()

    # Запускаем фоновую задачу после инициализации RabbitMQ
    new_notify_processor = await get_new_notification_processor()
    background_task = asyncio.create_task(new_notify_processor.process_new_notifications())

    yield

    # Отменяем фоновую задачу при завершении
    background_task.cancel()
    try:
        await background_task
    except asyncio.CancelledError:
        logger.info("Фоновая задача была успешно отменена")
    except Exception as e:
        logger.error(f"Возникла ошибка при завершении фонового процесса: {e}")

    await engine.dispose()

    if rabbitmq.producer:
        await rabbitmq.producer.close()
