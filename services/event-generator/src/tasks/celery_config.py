from celery import Celery
from core.config import app_config

celery_engine = Celery(
    "tasks",
    broker=app_config.rabbitmq.get_host,
    include=[
        "tasks.scheduled",
    ],
)

# Расписание запуска задач для celery beat
# Ключ в словаре может быть любым, а внутри "task": <value> value должно быть названием таски
celery_engine.conf.beat_schedule = {
    "issue.test_reminder_get_fresh_films_10_seconds": {
        "task": "issue.test_reminder_get_fresh_films_10_seconds",
        "schedule": app_config.celery_intervals["test_reminder_get_fresh_films_10_seconds"],
    },
    "issue.reminder_get_fresh_films_each_friday": {
        "task": "issue.reminder_get_fresh_films_each_friday",
        "schedule": app_config.celery_intervals["reminder_get_fresh_films_each_friday"],
    },
}
