#!/bin/sh
echo "Запуск waiters..."
python3 tests/functional/utils/wait_for_redis.py
python3 tests/functional/utils/wait_for_postgres.py
python3 tests/functional/utils/wait_for_auth-api.py

echo "Запуск тестов..."

pytest tests/functional/src -v -rP
echo "Повторный запуск провалившихся тестов через 5 сек..."
sleep 5
pytest tests/functional/src -v --last-failed -rP
