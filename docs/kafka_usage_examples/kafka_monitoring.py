# Нашёл интересную реализацию мониторинга. Но не хватило времени прикрутить в сервис.
# Нужно позже разобраться с этим.
"""
Утилиты для мониторинга Kafka консюмера.
"""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class ConsumerMetrics:
    """Метрики консюмера Kafka."""

    messages_processed: int = 0
    messages_failed: int = 0
    processing_time_total: float = 0.0
    last_message_time: Optional[float] = None
    start_time: float = field(default_factory=time.time)
    errors_by_topic: Dict[str, int] = field(default_factory=dict)

    @property
    def average_processing_time(self) -> float:
        """Среднее время обработки одного сообщения."""
        if self.messages_processed == 0:
            return 0.0
        return self.processing_time_total / self.messages_processed

    @property
    def messages_per_second(self) -> float:
        """Количество сообщений в секунду."""
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0.0
        return self.messages_processed / elapsed

    @property
    def error_rate(self) -> float:
        """Процент ошибок."""
        total = self.messages_processed + self.messages_failed
        if total == 0:
            return 0.0
        return (self.messages_failed / total) * 100

    def log_stats(self) -> None:
        """Логировать статистику."""
        logger.info(
            f"Consumer Stats: "
            f"Processed: {self.messages_processed}, "
            f"Failed: {self.messages_failed}, "
            f"Error Rate: {self.error_rate:.2f}%, "
            f"Avg Processing Time: {self.average_processing_time:.3f}s, "
            f"Messages/sec: {self.messages_per_second:.2f}"
        )


class MonitoredKafkaConsumer:
    """Kafka консюмер с мониторингом."""

    def __init__(self, consumer_manager, metrics: Optional[ConsumerMetrics] = None):
        self.consumer_manager = consumer_manager
        self.metrics = metrics or ConsumerMetrics()
        self._monitoring_task: Optional[asyncio.Task] = None
        self._monitor_interval = 60  # секунд

    async def start_monitoring(self) -> None:
        """Запустить мониторинг."""
        if self._monitoring_task is not None:
            return

        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Мониторинг консюмера запущен")

    async def stop_monitoring(self) -> None:
        """Остановить мониторинг."""
        if self._monitoring_task is not None:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
        logger.info("Мониторинг консюмера остановлен")

    async def _monitoring_loop(self) -> None:
        """Цикл мониторинга."""
        try:
            while True:
                await asyncio.sleep(self._monitor_interval)
                self.metrics.log_stats()

                # Проверка на простой
                if self.metrics.last_message_time:
                    idle_time = time.time() - self.metrics.last_message_time
                    if idle_time > 300:  # 5 минут без сообщений
                        logger.warning(f"Consumer простаивает {idle_time:.0f} секунд")

        except asyncio.CancelledError:
            pass

    async def tracked_message_handler(self, original_handler, topic: str, message: bytes) -> None:
        """Обработчик сообщений с отслеживанием метрик."""
        start_time = time.time()

        try:
            await original_handler(topic, message)

            # Обновляем метрики успеха
            processing_time = time.time() - start_time
            self.metrics.messages_processed += 1
            self.metrics.processing_time_total += processing_time
            self.metrics.last_message_time = time.time()

        except Exception as e:
            # Обновляем метрики ошибок
            self.metrics.messages_failed += 1
            self.metrics.errors_by_topic[topic] = self.metrics.errors_by_topic.get(topic, 0) + 1

            logger.error(f"Ошибка обработки сообщения из {topic}: {e}", exc_info=True)
            raise

    async def consume_with_monitoring(self, message_handler, **kwargs) -> None:
        """Запустить потребление с мониторингом."""

        # Оборачиваем обработчик для отслеживания метрик
        async def wrapped_handler(topic: str, message: bytes) -> None:
            await self.tracked_message_handler(message_handler, topic, message)

        await self.start_monitoring()

        try:
            await self.consumer_manager.consume_messages(wrapped_handler, **kwargs)
        finally:
            await self.stop_monitoring()


class HealthChecker:
    """Проверка здоровья Kafka консюмера."""

    def __init__(self, consumer_manager):
        self.consumer_manager = consumer_manager

    async def check_health(self) -> Dict[str, Any]:
        """Проверить здоровье консюмера."""
        health_status: Dict[str, Any] = {
            "status": "unknown",
            "consumer_running": False,
            "last_check": time.time(),
            "details": {},
        }

        try:
            # Проверяем статус консюмера
            health_status["consumer_running"] = self.consumer_manager.is_running

            if not self.consumer_manager.is_running:
                health_status["status"] = "unhealthy"
                health_status["details"]["error"] = "Consumer не запущен"
                return health_status

            # Дополнительные проверки можно добавить здесь
            # Например, проверка последнего времени получения сообщения

            health_status["status"] = "healthy"

        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["details"]["error"] = str(e)
            logger.error(f"Ошибка проверки здоровья: {e}", exc_info=True)

        return health_status


# Пример интеграции с FastAPI для health check endpoint
async def kafka_health_endpoint(consumer_manager):
    """Endpoint для проверки здоровья Kafka консюмера."""
    health_checker = HealthChecker(consumer_manager)
    health_status = await health_checker.check_health()

    if health_status["status"] != "healthy":
        # В FastAPI это будет возвращать 503 статус
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail=health_status)

    return health_status
