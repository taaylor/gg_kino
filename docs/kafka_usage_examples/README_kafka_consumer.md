# Улучшенный Kafka Consumer

Это улучшенная реализация асинхронного Kafka консюмера для сервиса recs-profile с расширенной функциональностью и надежностью.

## Основные улучшения

### 1. Устранены проблемы Singleton паттерна
- ✅ Правильная реализация Singleton с учетом параметров
- ✅ Возможность пересоздания консюмера с новыми параметрами

### 2. Улучшенная обработка ошибок
- ✅ Backoff с jitter для переподключений
- ✅ Отдельная обработка разных типов ошибок Kafka
- ✅ Безопасная обработка сообщений с логированием ошибок

### 3. Graceful shutdown
- ✅ Корректное завершение работы консюмера
- ✅ Контекстный менеджер для автоматического управления жизненным циклом
- ✅ Обработка сигналов отмены

### 4. Батчевая обработка
- ✅ Получение и обработка сообщений батчами
- ✅ Настраиваемый размер батча
- ✅ Параллельная обработка сообщений в батче

### 5. Конфигурация из настроек приложения
- ✅ Использование конфигурации из `app_config`
- ✅ Настройки таймаутов, retry, security
- ✅ Динамическое получение топиков

### 6. Типизация
- ✅ Полная типизация с Protocol для message handler
- ✅ Type hints для всех методов
- ✅ Поддержка mypy

### 7. Мониторинг и метрики
- ✅ Сбор метрик производительности
- ✅ Health check endpoints
- ✅ Логирование статистики

## Использование

### Базовое использование

```python
import asyncio
from utils.aiokafka_conn import create_consumer

async def my_message_handler(topic: str, message: bytes) -> None:
    """Обработчик сообщений."""
    data = json.loads(message.decode('utf-8'))
    print(f"Получено сообщение из {topic}: {data}")

async def main():
    consumer = create_consumer()

    # Рекомендуемый способ - использование контекстного менеджера
    async with consumer.consumer_context():
        await consumer.consume_messages(my_message_handler)

if __name__ == "__main__":
    asyncio.run(main())
```

### Использование с мониторингом

```python
from utils.kafka_monitoring import MonitoredKafkaConsumer, ConsumerMetrics

async def main_with_monitoring():
    consumer = create_consumer()
    metrics = ConsumerMetrics()
    monitored_consumer = MonitoredKafkaConsumer(consumer, metrics)

    async with consumer.consumer_context():
        await monitored_consumer.consume_with_monitoring(my_message_handler)
```

### Кастомная конфигурация

```python
from utils.aiokafka_conn import KafkaConsumerManager

# Создание консюмера с кастомными настройками
consumer = KafkaConsumerManager(
    topics=["custom-topic-1", "custom-topic-2"],
    group_id="custom-group",
    bootstrap_servers=["kafka1:9092", "kafka2:9092"],
    # Дополнительные параметры aiokafka
    auto_offset_reset="earliest",
    enable_auto_commit=False,
)
```

### Health Check для FastAPI

```python
from fastapi import FastAPI
from utils.kafka_monitoring import kafka_health_endpoint

app = FastAPI()

@app.get("/health/kafka")
async def kafka_health():
    consumer = create_consumer()
    return await kafka_health_endpoint(consumer)
```

## Конфигурация

Консюмер использует настройки из `core.config.app_config.kafka`:

```python
class Kafka(BaseModel):
    host1: str = "localhost"
    port1: int = 9094
    host2: str = "localhost"
    port2: int = 9095
    host3: str = "localhost"
    port3: int = 9096

    retry_backoff_ms: int = 100
    request_timeout_ms: int = 5000
    batch_size: int = 5120
    linger_ms: int = 5
    buffer_memory: int = 33554432
    security_protocol: str = "PLAINTEXT"

    rec_bookmarks_list_topic: str = "user_content_add_film_to_bookmarks_event"
    rec_user_ratings_films_topic: str = "user_content_users_ratings_films_event"
```

## Основные классы

### KafkaConsumerManager
Основной класс для управления Kafka консюмером:
- `start()` - запуск консюмера
- `stop()` - остановка консюмера
- `consume_messages()` - потребление сообщений
- `consumer_context()` - контекстный менеджер

### MessageHandler Protocol
Протокол для обработчика сообщений:
```python
class MessageHandler(Protocol):
    async def __call__(self, topic: str, message: bytes) -> None:
        ...
```

### MonitoredKafkaConsumer
Консюмер с мониторингом метрик:
- Подсчет обработанных/неудачных сообщений
- Среднее время обработки
- Количество сообщений в секунду
- Процент ошибок

### ConsumerMetrics
Класс для сбора метрик:
- `messages_processed` - количество обработанных сообщений
- `messages_failed` - количество неудачных сообщений
- `average_processing_time` - среднее время обработки
- `messages_per_second` - сообщений в секунду
- `error_rate` - процент ошибок

## Лучшие практики

1. **Используйте контекстный менеджер** для автоматического управления жизненным циклом
2. **Обрабатывайте ошибки** в message handler - они логируются, но не прерывают работу
3. **Настройте батчи** - используйте `max_messages_per_batch` для оптимизации производительности
4. **Мониторьте метрики** - используйте `MonitoredKafkaConsumer` в продакшене
5. **Graceful shutdown** - обрабатывайте KeyboardInterrupt и другие сигналы

## Примеры ошибок и их обработка

Консюмер автоматически обрабатывает:
- `KafkaConnectionError` - переподключение с backoff
- `KafkaTimeoutError` - переподключение с backoff
- `ConsumerStoppedError` - корректное завершение
- JSON deserialization errors - логирование без остановки
- Handler exceptions - логирование без остановки

## Миграция со старого кода

Старый код:
```python
consumer = KafkaConsumerSingleton(topics, group_id, servers)
await consumer.start()
await consumer.run(handler)
await consumer.stop()
```

Новый код:
```python
consumer = create_consumer()  # или KafkaConsumerManager(...)
async with consumer.consumer_context():
    await consumer.consume_messages(handler)
```
