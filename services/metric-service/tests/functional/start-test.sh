#!/bin/sh

echo "Запуск тестов..."
sleep 5
pytest ./tests/functional/src -v -rP
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo "Обнаружены провалившиеся тесты. Повторный запуск через 5 сек..."
    sleep 5
    pytest ./tests/functional/src -v --last-failed -rP
else
    echo "Все тесты пройдены успешно!"
fi
