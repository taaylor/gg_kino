#!/usr/bin/env bash

MODEL="${LLM_MODEL}"

echo "🧠 Запускаем Ollama (serve) в фоне..."
ollama serve &
PID=$!

echo "⏳ Ждём, пока сервис будет готов..."
until curl -s http://localhost:11434/api/version > /dev/null; do sleep 1; done

echo "🔁 Проверяем, запущена ли модель ${MODEL}..."
if curl -s http://localhost:11434/api/ps \
     | grep -q "\"name\":\"${MODEL}\""; then
  echo "✅ Модель ${MODEL} уже загружена."
else
  echo "🚀 Модель ${MODEL} не найдена — запускаем..."
  ollama run "${MODEL}"
fi

wait $PID
