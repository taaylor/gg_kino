from celery import Celery
from core.config import app_config

celery_engine = Celery(
    "tasks",
    broker=app_config.redis.get_redis_host,
    include=[
        "tasks.scheduled",
    ],
)

celery_engine.conf.beat_schedule = {
    "issue.reminder_task_etl": {
        "task": "issue.reminder_task_etl",
        "schedule": app_config.time_start_etl_seconds,  # раз в сутки
    },
}
