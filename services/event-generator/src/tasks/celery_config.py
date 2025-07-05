import os

from celery import Celery

# from celery.schedules import crontab

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "pass")

celery_engine = Celery(
    "tasks",
    broker=f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@rabbitmq-1:5672//",
    include=[
        "tasks.scheduled",
    ],
)

# Расписание запуска задач для celery beat
# Ключ в словаре может быть любым, а внутри "task": <value> value должно быть названием таски
celery_engine.conf.beat_schedule = {
    "issue.reminder_1day": {
        "task": "issue.reminder_1day",
        "schedule": 10,  # каждые 10 секнд
        # "schedule": crontab(minute="0", hour="9"),  # каждое утро в 9:00
    },
    # "luboe-nazvanie": {
    #     "task": "periodic_task",
    #     "schedule": 5,  # секунды
    #     # "schedule": crontab(minute="30", hour="15"),
    # }
}
