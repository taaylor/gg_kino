import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from core.config import app_config
from db import postgres
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from utils.aiokafka_conn import create_consumer_manager

logger = logging.getLogger(__name__)


async def monitor_tasks(task: asyncio.Task, task_name: str) -> None:
    try:
        await task
    except asyncio.CancelledError:
        logger.info(f"Фоновая задача '{task_name}' была успешно отменена")
    except Exception as e:
        logger.error(f"Возникла ошибка при выполнении фоновой задачи '{task_name}': {e}")
        raise e


# Временная функция
async def message_handler(topic: str, message: bytes):
    logger.info(f"Получено сообщение из топика: {topic}, содержание: {message.decode("utf-8")} ")


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

    kafka_manager = create_consumer_manager()

    await kafka_manager.start()
    await kafka_manager.consume_messages(message_handler)

    yield

    await kafka_manager.stop()

    await engine.dispose()
