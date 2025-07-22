from celery import Celery
from core.config import app_config

# redis://[<user>[:<password>]@]<host>[:<port>]/<db>
celery_engine = Celery(
    "tasks",
    broker=app_config.redis.get_redis_host,
    # broker="redis://redis_user:Parol123@redis:6379/1",
    include=[
        "tasks.scheduled",
    ],
)

# Расписание запуска задач для celery beat
# Ключ в словаре может быть любым, а внутри "task": <value> value должно быть названием таски
celery_engine.conf.beat_schedule = {
    "issue.test_reminder_get_data": {
        "task": "issue.test_reminder_get_data",
        "schedule": 10,
    },
    # "issue.reminder_get_fresh_films_each_friday": {
    #     "task": "issue.reminder_get_fresh_films_each_friday",
    #     "schedule": app_config.celery_intervals["reminder_get_fresh_films_each_friday"],
    # },
}
