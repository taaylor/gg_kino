# import asyncio
# from pprint import pprint as pp

from core.logger_config import get_logger
from tasks.celery_config import celery_engine

logger = get_logger(__name__)


@celery_engine.task(name="issue.test_reminder_get_data")
def remind_10_seconds():
    logger.info("logging from celery task")
    return True


# @celery_engine.task(name="issue.reminder_get_fresh_films_each_friday")
# def remind_each_friday():
#     film_sheduler = get_film_scheduler_service()
#     result = asyncio.run(film_sheduler.execute_task())
#     pp(result)  # временно, чтобы видеть, что запрос выпоняется
#     return True
