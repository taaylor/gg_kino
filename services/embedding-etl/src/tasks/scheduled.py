import asyncio

from core.logger_config import get_logger
from run_etl import main
from tasks.celery_config import celery_engine

logger = get_logger(__name__)


@celery_engine.task(name="issue.reminder_task_etl")
def remind_10_seconds():
    logger.info("Начало запуска ETL")
    asyncio.run(main())
    logger.info("ETL отработал")
    return True
