#!/bin/bash
set -e

alembic upgrade head

python dump_templates.py

python main.py
