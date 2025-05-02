#!/bin/bash

SERVICE_NAME="auth-api"

# Проверка, что docker запущен
if ! sudo docker info >/dev/null 2>&1; then
  echo "❌ Docker не запущен."
  exit 1
fi

# Проверка, что docker-compose доступен
if ! sudo docker compose ps >/dev/null 2>&1; then
  echo "❌ docker-compose не запущен или не найден docker-compose.yml."
  exit 1
fi

# Проверка, что сервис auth-api запущен
if ! sudo docker compose ps "$SERVICE_NAME" | grep -q "Up"; then
  echo "❌ Сервис $SERVICE_NAME не запущен. Пожалуйста, запустите docker compose:"
  echo "docker compose up --build -d"
  exit 1
fi

sudo docker compose exec "$SERVICE_NAME" python manage.py createsuperuser
