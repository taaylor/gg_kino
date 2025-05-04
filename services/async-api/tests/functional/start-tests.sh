#!/bin/sh

echo "Запуск waiters..."
python3 ./tests/functional/utils/wait_for_es.py
python3 ./tests/functional/utils/wait_for_redis.py
python3 ./tests/functional/utils/wait_for_postgres.py
python3 ./tests/functional/utils/wait_for_api.py
python3 ./tests/functional/utils/wait_for_auth-api.py

echo "Запуск тестов..."

pytest ./tests/functional/src -v -rP
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo "Обнаружены провалившиеся тесты. Повторный запуск через 5 сек..."
    sleep 5
    pytest ./tests/functional/src -v --last-failed -rP
else
    echo "Все тесты пройдены успешно!"
fi
