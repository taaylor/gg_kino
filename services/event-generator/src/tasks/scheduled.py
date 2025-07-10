import asyncio
from pprint import pprint as pp

from services.notification_sheduler_service import get_film_scheduler_service
from tasks.celery_config import celery_engine


@celery_engine.task(name="issue.test_reminder_get_fresh_films_10_seconds")
def remind_10_seconds():
    film_sheduler = get_film_scheduler_service()
    result = asyncio.run(film_sheduler.execute_task())
    pp(result)  # временно, чтобы видеть, что запрос выпоняется
    return True


@celery_engine.task(name="issue.reminder_get_fresh_films_each_friday")
def remind_each_friday():
    film_sheduler = get_film_scheduler_service()
    result = asyncio.run(film_sheduler.execute_task())
    pp(result)  # временно, чтобы видеть, что запрос выпоняется
    return True
