# Kafka Configuration

## Использование переменных из .env файла

Данная конфигурация использует переменные окружения из файла `.env` в корне проекта для настройки имен топиков Kafka.

### Переменные топиков в .env:

```env
LIKE_TOPIC=user_metric_like_event
COMMENT_TOPIC=user_metric_comment_event
WATCH_PROGRESS_TOPIC=user_metric_watch_progress_event
WATCH_LIST_TOPIC=user_metric_add_to_watch_list_event
OTHER_TOPIC=user_metric_other_event
```

### Запуск Kafka:

Из корня проекта:
```bash
docker-compose -f infra/kafka/docker-compose.kafka.yaml up -d
```

### Изменение имен топиков:

1. Отредактируйте переменные в файле `.env` в корне проекта
2. Пересоздайте контейнеры:
   ```bash
   docker-compose -f infra/kafka/docker-compose.kafka.yaml down -v
   docker-compose -f infra/kafka/docker-compose.kafka.yaml up -d
   ```

### Доступ к Kafka UI:

После запуска Kafka UI будет доступен по адресу: http://localhost:8080

### Структура:

- **kafka-0, kafka-1, kafka-2**: Брокеры Kafka в кластере
- **kafka-init**: Инициализация топиков с именами из переменных окружения
- **ui**: Kafka UI для мониторинга и управления
