import asyncio
from pprint import pprint as pp

from services.notification_sheduler_service import FilmSchedulerService
from tasks.celery_config import celery_engine


@celery_engine.task(name="issue.reminder_1day")
def remind_1day():
    result = asyncio.run(FilmSchedulerService.execute_task())
    pp(result)  # временно, чтобы видеть, что запрос выпоняется
    return True


async def get_data():
    await asyncio.sleep(5)


# @celery_engine.task(name="periodic_task")
def periodic_task():
    """Пример запуска асинхронной функции внутри celery таски"""
    print(12345)
    asyncio.run(get_data())
