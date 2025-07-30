"""
Тесты для улучшенного Kafka консюмера.
"""

import asyncio
import json
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from utils.aiokafka_conn import KafkaConsumerManager, create_consumer
from utils.kafka_monitoring import ConsumerMetrics, MonitoredKafkaConsumer


class TestKafkaConsumerManager:
    """Тесты для KafkaConsumerManager."""

    @pytest.fixture
    def consumer_manager(self):
        """Фикстура для создания консюмера."""
        return KafkaConsumerManager(
            topics=["test-topic-1", "test-topic-2"],
            group_id="test-group",
            bootstrap_servers=["localhost:9092"],
        )

    @pytest.fixture
    def mock_kafka_consumer(self):
        """Мок для AIOKafkaConsumer."""
        with patch("utils.aiokafka_conn.AIOKafkaConsumer") as mock:
            mock_instance = AsyncMock()
            mock.return_value = mock_instance
            yield mock_instance

    async def test_consumer_creation(self, consumer_manager):
        """Тест создания консюмера."""
        assert consumer_manager._topics == ["test-topic-1", "test-topic-2"]
        assert consumer_manager._group_id == "test-group"
        assert consumer_manager._bootstrap_servers == ["localhost:9092"]
        assert not consumer_manager.is_running

    async def test_start_stop_consumer(self, consumer_manager, mock_kafka_consumer):
        """Тест запуска и остановки консюмера."""
        # Запуск
        await consumer_manager.start()
        assert consumer_manager.is_running
        mock_kafka_consumer.start.assert_called_once()

        # Остановка
        await consumer_manager.stop()
        assert not consumer_manager.is_running
        mock_kafka_consumer.stop.assert_called_once()

    async def test_context_manager(self, consumer_manager, mock_kafka_consumer):
        """Тест контекстного менеджера."""
        async with consumer_manager.consumer_context():
            assert consumer_manager.is_running
            mock_kafka_consumer.start.assert_called_once()

        assert not consumer_manager.is_running
        mock_kafka_consumer.stop.assert_called_once()

    async def test_message_processing(self, consumer_manager, mock_kafka_consumer):
        """Тест обработки сообщений."""
        # Подготавливаем моки сообщений
        mock_message1 = MagicMock()
        mock_message1.topic = "test-topic-1"
        mock_message1.value = b'{"user_id": 1, "action": "test"}'

        mock_message2 = MagicMock()
        mock_message2.topic = "test-topic-2"
        mock_message2.value = b'{"user_id": 2, "action": "test2"}'

        # Настраиваем getmany для возврата сообщений один раз, затем пустые результаты
        mock_kafka_consumer.getmany.side_effect = [
            {"tp1": [mock_message1, mock_message2]},  # Первый вызов - сообщения
            {},  # Последующие вызовы - пустые результаты
        ]

        # Мок обработчика
        handler = AsyncMock()

        # Запускаем консюмер
        await consumer_manager.start()

        # Создаем задачу для обработки сообщений и отменяем её через короткое время
        consume_task = asyncio.create_task(
            consumer_manager.consume_messages(handler, max_messages_per_batch=10)
        )

        # Даем время на обработку
        await asyncio.sleep(0.1)

        # Останавливаем консюмер
        await consumer_manager.stop()
        consume_task.cancel()

        try:
            await consume_task
        except asyncio.CancelledError:
            pass

        # Проверяем, что обработчик был вызван
        assert handler.call_count >= 2
        handler.assert_any_call("test-topic-1", b'{"user_id": 1, "action": "test"}')
        handler.assert_any_call("test-topic-2", b'{"user_id": 2, "action": "test2"}')

    async def test_error_handling_in_handler(self, consumer_manager, mock_kafka_consumer):
        """Тест обработки ошибок в handler."""
        mock_message = MagicMock()
        mock_message.topic = "test-topic"
        mock_message.value = b'{"test": "data"}'

        mock_kafka_consumer.getmany.side_effect = [
            {"tp1": [mock_message]},
            {},
        ]

        # Обработчик, который выбрасывает исключение
        async def failing_handler(topic: str, message: bytes) -> None:
            raise ValueError("Test error")

        await consumer_manager.start()

        consume_task = asyncio.create_task(consumer_manager.consume_messages(failing_handler))

        await asyncio.sleep(0.1)
        await consumer_manager.stop()
        consume_task.cancel()

        try:
            await consume_task
        except asyncio.CancelledError:
            pass

        # Консюмер должен продолжить работу даже при ошибках в обработчике

    async def test_factory_function(self):
        """Тест фабричной функции create_consumer."""
        consumer1 = create_consumer()
        consumer2 = create_consumer()

        # Каждый вызов создает новый экземпляр
        assert consumer1 is not consumer2
        assert isinstance(consumer1, KafkaConsumerManager)
        assert isinstance(consumer2, KafkaConsumerManager)


class TestConsumerMetrics:
    """Тесты для метрик консюмера."""

    def test_initial_metrics(self):
        """Тест начальных значений метрик."""
        metrics = ConsumerMetrics()

        assert metrics.messages_processed == 0
        assert metrics.messages_failed == 0
        assert metrics.processing_time_total == 0.0
        assert metrics.last_message_time is None
        assert metrics.average_processing_time == 0.0
        assert metrics.messages_per_second == 0.0
        assert metrics.error_rate == 0.0

    def test_metrics_calculation(self):
        """Тест расчета метрик."""
        metrics = ConsumerMetrics()

        # Симулируем обработку сообщений
        metrics.messages_processed = 10
        metrics.messages_failed = 2
        metrics.processing_time_total = 5.0

        assert metrics.average_processing_time == 0.5
        assert metrics.error_rate == (2 / 12) * 100  # 2 failed out of 12 total

    def test_metrics_with_zero_messages(self):
        """Тест метрик при отсутствии сообщений."""
        metrics = ConsumerMetrics()

        assert metrics.average_processing_time == 0.0
        assert metrics.messages_per_second == 0.0
        assert metrics.error_rate == 0.0


class TestMonitoredKafkaConsumer:
    """Тесты для консюмера с мониторингом."""

    @pytest.fixture
    def mock_consumer_manager(self):
        """Мок для консюмера."""
        return AsyncMock()

    async def test_monitored_consumer_creation(self, mock_consumer_manager):
        """Тест создания консюмера с мониторингом."""
        monitored = MonitoredKafkaConsumer(mock_consumer_manager)

        assert monitored.consumer_manager is mock_consumer_manager
        assert isinstance(monitored.metrics, ConsumerMetrics)

    async def test_successful_message_handling(self, mock_consumer_manager):
        """Тест успешной обработки сообщения."""
        monitored = MonitoredKafkaConsumer(mock_consumer_manager)

        async def test_handler(topic: str, message: bytes) -> None:
            # Симулируем небольшую обработку
            await asyncio.sleep(0.01)

        # Обрабатываем сообщение
        await monitored.tracked_message_handler(test_handler, "test-topic", b'{"test": "data"}')

        # Проверяем метрики
        assert monitored.metrics.messages_processed == 1
        assert monitored.metrics.messages_failed == 0
        assert monitored.metrics.processing_time_total > 0
        assert monitored.metrics.last_message_time is not None

    async def test_failed_message_handling(self, mock_consumer_manager):
        """Тест обработки сообщения с ошибкой."""
        monitored = MonitoredKafkaConsumer(mock_consumer_manager)

        async def failing_handler(topic: str, message: bytes) -> None:
            raise ValueError("Test error")

        # Обработка должна выбросить исключение
        with pytest.raises(ValueError):
            await monitored.tracked_message_handler(
                failing_handler, "test-topic", b'{"test": "data"}'
            )

        # Проверяем метрики
        assert monitored.metrics.messages_processed == 0
        assert monitored.metrics.messages_failed == 1
        assert monitored.metrics.errors_by_topic["test-topic"] == 1


# Интеграционные тесты (требуют запущенный Kafka)
@pytest.mark.integration
class TestKafkaIntegration:
    """Интеграционные тесты с реальным Kafka."""

    @pytest.fixture
    async def kafka_consumer(self):
        """Фикстура для интеграционных тестов."""
        consumer = KafkaConsumerManager(
            topics=["integration-test-topic"],
            group_id="integration-test-group",
            bootstrap_servers=["localhost:9092"],
        )

        yield consumer

        # Cleanup
        if consumer.is_running:
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_real_kafka_connection(self, kafka_consumer):
        """Тест подключения к реальному Kafka."""
        try:
            await kafka_consumer.start()
            assert kafka_consumer.is_running
        except Exception as e:
            pytest.skip(f"Kafka недоступен: {e}")
        finally:
            await kafka_consumer.stop()


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])
