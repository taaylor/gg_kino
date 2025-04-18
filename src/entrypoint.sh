#!/bin/bash
alembic upgrade head
exec gunicorn main:app --config ./core/gunicorn_conf.py