#!/bin/bash
set -e

# 1) Прогон миграций
alembic upgrade head

python main.py
# 2) Запуск Celery
# if [[ "$1" == "celery" ]]; then
#     exec celery --app=tasks.celery_config:celery_engine worker -l INFO
# elif [[ "$1" == "celery_beat" ]]; then
#     exec celery --app=tasks.celery_config:celery_engine worker -l INFO -B
# elif [[ "$1" == "flower" ]]; then
#     exec celery --app=tasks.celery_config:celery_engine flower
# else
#     echo "Usage: $0 {celery|celery_beat|flower}"
#     exit 1
# fi
