#!/usr/bin/env bash

set -e

chown www-data:www-data /var/log

cd /opt/app && python manage.py migrate --noinput

python manage.py collectstatic --noinput

cp -r /opt/app/static/ /var/www/static/

# gunicorn --bind 0.0.0.0:8000 config.wsgi
python -m debugpy --listen 0.0.0.0:5678 manage.py runserver 0.0.0.0:8002
