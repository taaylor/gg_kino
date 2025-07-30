"""
Полный пример интеграции улучшенного Kafka консюмера с типизированными сообщениями.
"""

import asyncio
import logging
import signal
from contextlib import asynccontextmanager
from typing import Optional

from schemas.kafka_messages import typed_message_handler
from utils.aiokafka_conn import create_consumer
from utils.kafka_monitoring import ConsumerMetrics, MonitoredKafkaConsumer

logger = logging.getLogger(__name__)


class RecsProfileKafkaService:
    """Сервис для обработки Kafka сообщений в recs-profile."""

    def __init__(self):
        self.consumer = create_consumer()
        self.metrics = ConsumerMetrics()
        self.monitored_consumer = MonitoredKafkaConsumer(self.consumer, self.metrics)
        self._shutdown_event = asyncio.Event()
        self._running = False

    async def start(self) -> None:
        """Запустить сервис."""
        if self._running:
            logger.warning("Сервис уже запущен")
            return

        logger.info("Запуск Kafka сервиса recs-profile...")

        try:
            # Настраиваем обработку сигналов для graceful shutdown
            self._setup_signal_handlers()

            # Запускаем консюмер с мониторингом
            async with self.consumer.consumer_context():
                self._running = True
                logger.info("Kafka сервис запущен, ожидание сообщений...")

                # Запускаем обработку сообщений
                await self.monitored_consumer.consume_with_monitoring(
                    typed_message_handler,
                    max_messages_per_batch=50,  # Оптимизируем для производительности
                )

        except asyncio.CancelledError:
            logger.info("Получен сигнал отмены")
        except Exception as e:
            logger.error(f"Критическая ошибка в Kafka сервисе: {e}", exc_info=True)
            raise
        finally:
            self._running = False
            logger.info("Kafka сервис остановлен")

    async def stop(self) -> None:
        """Остановить сервис."""
        if not self._running:
            return

        logger.info("Остановка Kafka сервиса...")
        self._shutdown_event.set()

    def _setup_signal_handlers(self) -> None:
        """Настроить обработчики сигналов для graceful shutdown."""
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, self._signal_handler)
        if hasattr(signal, "SIGINT"):
            signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame) -> None:
        """Обработчик сигналов."""
        logger.info(f"Получен сигнал {signum}, инициируем остановку...")
        asyncio.create_task(self.stop())

    @property
    def is_running(self) -> bool:
        """Проверить, запущен ли сервис."""
        return self._running

    def get_metrics(self) -> dict:
        """Получить метрики сервиса."""
        return {
            "is_running": self.is_running,
            "consumer_running": self.consumer.is_running,
            "messages_processed": self.metrics.messages_processed,
            "messages_failed": self.metrics.messages_failed,
            "error_rate": self.metrics.error_rate,
            "average_processing_time": self.metrics.average_processing_time,
            "messages_per_second": self.metrics.messages_per_second,
            "errors_by_topic": dict(self.metrics.errors_by_topic),
        }


# Глобальный экземпляр сервиса
_kafka_service: Optional[RecsProfileKafkaService] = None


def get_kafka_service() -> RecsProfileKafkaService:
    """Получить глобальный экземпляр Kafka сервиса."""
    global _kafka_service
    if _kafka_service is None:
        _kafka_service = RecsProfileKafkaService()
    return _kafka_service


@asynccontextmanager
async def kafka_service_lifespan():
    """Контекстный менеджер для управления жизненным циклом Kafka сервиса."""
    service = get_kafka_service()
    service_task = None

    try:
        # Запускаем сервис в отдельной задаче
        service_task = asyncio.create_task(service.start())

        # Даем время на запуск
        await asyncio.sleep(1)

        if not service.is_running:
            raise RuntimeError("Не удалось запустить Kafka сервис")

        yield service

    finally:
        # Останавливаем сервис
        await service.stop()

        # Ждем завершения задачи
        if service_task is not None:
            service_task.cancel()
            try:
                await service_task
            except asyncio.CancelledError:
                pass


# Интеграция с FastAPI
def setup_kafka_routes(app):
    """Настроить роуты для мониторинга Kafka в FastAPI."""

    @app.get("/health/kafka")
    async def kafka_health():
        """Health check для Kafka сервиса."""
        service = get_kafka_service()
        metrics = service.get_metrics()

        if not metrics["consumer_running"]:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=503,
                detail={
                    "status": "unhealthy",
                    "reason": "Kafka consumer не запущен",
                    "metrics": metrics,
                },
            )

        return {"status": "healthy", "metrics": metrics}

    @app.get("/metrics/kafka")
    async def kafka_metrics():
        """Получить метрики Kafka сервиса."""
        service = get_kafka_service()
        return service.get_metrics()


# Интеграция с FastAPI через lifespan events
async def kafka_startup_event():
    """Событие запуска для FastAPI."""
    logger.info("Запуск Kafka сервиса при старте приложения...")
    service = get_kafka_service()

    # Запускаем сервис в фоновой задаче
    asyncio.create_task(service.start())

    # Даем время на запуск
    await asyncio.sleep(2)

    if not service.is_running:
        logger.error("Не удалось запустить Kafka сервис")
        raise RuntimeError("Kafka сервис не запустился")

    logger.info("Kafka сервис успешно запущен")


async def kafka_shutdown_event():
    """Событие остановки для FastAPI."""
    logger.info("Остановка Kafka сервиса...")
    service = get_kafka_service()
    await service.stop()
    logger.info("Kafka сервис остановлен")


# Standalone запуск
async def main():
    """Основная функция для standalone запуска."""
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger.info("Запуск recs-profile Kafka сервиса...")

    try:
        async with kafka_service_lifespan() as service:
            logger.info("Сервис запущен. Нажмите Ctrl+C для остановки")

            # Ждем сигнала остановки
            try:
                while service.is_running:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Получен сигнал остановки от пользователя")

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка приложения: {e}", exc_info=True)
        exit(1)
