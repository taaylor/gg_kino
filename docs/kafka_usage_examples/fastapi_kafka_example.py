"""
Пример интеграции Kafka консюмера с FastAPI приложением.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from schemas.kafka_messages import typed_message_handler
from utils.aiokafka_conn import KafkaConsumerManager, create_consumer
from utils.kafka_monitoring import ConsumerMetrics, MonitoredKafkaConsumer

logger = logging.getLogger(__name__)

# Глобальные переменные для консюмера
kafka_consumer: Optional[KafkaConsumerManager] = None
consumer_metrics: Optional[ConsumerMetrics] = None
monitored_consumer: Optional[MonitoredKafkaConsumer] = None
consumer_task: Optional[asyncio.Task] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    global kafka_consumer, consumer_metrics, monitored_consumer, consumer_task

    # Startup
    logger.info("Запуск Kafka консюмера...")

    try:
        # Создаем консюмер и метрики
        kafka_consumer = create_consumer()
        consumer_metrics = ConsumerMetrics()
        monitored_consumer = MonitoredKafkaConsumer(kafka_consumer, consumer_metrics)

        # Запускаем консюмер в фоновой задаче
        async def run_consumer():
            try:
                if kafka_consumer and monitored_consumer:
                    async with kafka_consumer.consumer_context():
                        await monitored_consumer.consume_with_monitoring(
                            typed_message_handler, max_messages_per_batch=50
                        )
            except Exception as e:
                logger.error(f"Ошибка в Kafka консюмере: {e}", exc_info=True)

        consumer_task = asyncio.create_task(run_consumer())

        # Даем время на запуск
        await asyncio.sleep(1)

        if not kafka_consumer.is_running:
            raise RuntimeError("Не удалось запустить Kafka консюмер")

        logger.info("Kafka консюмер успешно запущен")

        yield

    finally:
        # Shutdown
        logger.info("Остановка Kafka консюмера...")

        if consumer_task:
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                pass

        if kafka_consumer and kafka_consumer.is_running:
            await kafka_consumer.stop()

        logger.info("Kafka консюмер остановлен")


# Создаем FastAPI приложение с lifespan
app = FastAPI(
    title="Recs Profile Service",
    description="Сервис профилей и рекомендаций",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {"message": "Recs Profile Service"}


@app.get("/health")
async def health_check():
    """Общий health check."""
    return {
        "status": "healthy",
        "service": "recs-profile",
        "kafka_consumer_running": kafka_consumer.is_running if kafka_consumer else False,
    }


@app.get("/health/kafka")
async def kafka_health_check():
    """Health check для Kafka консюмера."""
    if not kafka_consumer:
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "reason": "Kafka консюмер не инициализирован"},
        )

    if not kafka_consumer.is_running:
        raise HTTPException(
            status_code=503, detail={"status": "unhealthy", "reason": "Kafka консюмер не запущен"}
        )

    return {
        "status": "healthy",
        "consumer_running": kafka_consumer.is_running,
        "topics": kafka_consumer._topics,
        "group_id": kafka_consumer._group_id,
    }


@app.get("/metrics/kafka")
async def kafka_metrics():
    """Получить метрики Kafka консюмера."""
    if not consumer_metrics:
        raise HTTPException(status_code=404, detail="Метрики не доступны")

    return {
        "messages_processed": consumer_metrics.messages_processed,
        "messages_failed": consumer_metrics.messages_failed,
        "error_rate": consumer_metrics.error_rate,
        "average_processing_time": consumer_metrics.average_processing_time,
        "messages_per_second": consumer_metrics.messages_per_second,
        "errors_by_topic": dict(consumer_metrics.errors_by_topic),
        "uptime_seconds": consumer_metrics.start_time,
        "last_message_time": consumer_metrics.last_message_time,
    }


# Эндпоинты для управления консюмером (для разработки/отладки)
@app.post("/admin/kafka/restart")
async def restart_kafka_consumer():
    """Перезапустить Kafka консюмер (только для разработки)."""
    global consumer_task

    if not kafka_consumer:
        raise HTTPException(status_code=404, detail="Консюмер не инициализирован")

    try:
        # Останавливаем текущую задачу
        if consumer_task:
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                pass

        # Останавливаем консюмер
        if kafka_consumer.is_running:
            await kafka_consumer.stop()

        # Запускаем заново
        async def run_consumer():
            if kafka_consumer and monitored_consumer:
                async with kafka_consumer.consumer_context():
                    await monitored_consumer.consume_with_monitoring(
                        typed_message_handler, max_messages_per_batch=50
                    )

        consumer_task = asyncio.create_task(run_consumer())
        await asyncio.sleep(1)

        if not kafka_consumer.is_running:
            raise HTTPException(status_code=500, detail="Не удалось перезапустить консюмер")

        return {"status": "restarted", "consumer_running": kafka_consumer.is_running}

    except Exception as e:
        logger.error(f"Ошибка при перезапуске консюмера: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка перезапуска: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Запускаем приложение
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
