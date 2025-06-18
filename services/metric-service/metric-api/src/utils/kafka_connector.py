import json
import logging
from contextlib import contextmanager
from typing import Any

import backoff
from core.config import app_config
from kafka import KafkaProducer
from kafka.errors import KafkaConnectionError, KafkaError, KafkaTimeoutError

logger = logging.getLogger(__name__)


class KafkaConnector:
    """Класс для управления подключениями к Kafka"""

    __slots__ = ("config", "_producer")

    def __init__(self) -> None:
        self.config = self._get_config()
        self._producer: KafkaProducer | None = None

    def _get_config(self) -> dict[str, Any]:
        return {
            "bootstrap_servers": app_config.kafka.get_servers,
            "client_id": app_config.project_name,
            "value_serializer": self._json_serializer,
            "key_serializer": lambda v: str(v).encode("utf-8") if v is not None else None,
            "acks": app_config.kafka.acks,
            "retries": app_config.kafka.retries,
            "retry_backoff_ms": app_config.kafka.retry_backoff_ms,
            "request_timeout_ms": app_config.kafka.request_timeout_ms,
            "batch_size": app_config.kafka.batch_size,
            "linger_ms": app_config.kafka.linger_ms,
            "buffer_memory": app_config.kafka.buffer_memory,
            "security_protocol": app_config.kafka.security_protocol,
        }

    @staticmethod
    def _json_serializer(value: Any) -> bytes:
        """Сериализация значений в JSON"""
        if isinstance(value, (str, bytes)):
            return value.encode("utf-8") if isinstance(value, str) else value
        return json.dumps(value, ensure_ascii=False).encode("utf-8")

    @backoff.on_exception(
        backoff.expo,
        (KafkaTimeoutError, KafkaConnectionError),
        max_tries=5,
        jitter=backoff.full_jitter,
        max_time=60,
    )
    def _create_producer(self) -> KafkaProducer:
        try:
            logger.debug(
                f"Создаю подключение к Kafka: {self.config["bootstrap_servers"]}",
            )
            producer = KafkaProducer(**self.config)
            logger.info("Kafka producer успешно создан")
            return producer
        except Exception as error:
            logger.error(f"Ошибка создания Kafka producer: {error}")
            raise

    def get_producer(self) -> KafkaProducer:
        """Получить Kafka producer (singleton)"""
        if self._producer is None:
            self._producer = self._create_producer()
        return self._producer

    def close(self):
        """Закрыть подключение к Kafka"""
        if self._producer:
            try:
                self._producer.flush()
                self._producer.close()
                logger.info("Kafka producer закрыт")
            except Exception as error:
                logger.error(f"Ошибка при закрытии Kafka producer: {error}")
            finally:
                self._producer = None

    @contextmanager
    def producer_context(self):
        """Контекстный менеджер для работы с producer"""
        producer = None
        try:
            producer = self.get_producer()
            yield producer
        finally:
            if producer:
                try:
                    producer.flush()
                except Exception as error:
                    logger.error(f"Ошибка при flush Kafka producer: {error}")

    def send_message(
        self,
        topic: str,
        value: Any,
        key: str | bytes | None = None,
        partition: int | None = None,
        timestamp_ms: int | None = None,
        headers: str | bytes | None = None,
    ) -> bool:
        """Отправить сообщение в Kafka

        Returns:
            bool: True если сообщение отправлено успешно

        """
        try:
            with self.producer_context() as producer:
                message = producer.send(
                    topic=topic,
                    value=value,
                    key=key,
                    partition=partition,
                    timestamp_ms=timestamp_ms,
                    headers=headers,
                )

                record_metadata = message.get(timeout=10)
                logger.debug(
                    f"Сообщение отправлено в топик {record_metadata.topic}, partition {record_metadata.partition}, offset {record_metadata.offset}"  # noqa E501
                )
                return True

        except KafkaTimeoutError:
            logger.error(f"Таймаут при отправке сообщения в топик {topic}")
            return False
        except KafkaError as error:
            logger.error(f"Ошибка Kafka при отправке в топик {topic}: {error}")
            return False
        except Exception as error:
            logger.error(f"Неожиданная ошибка при отправке в топик {topic}: {error}")
            return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Глобальный экземпляр коннектора
_kafka_connector: KafkaConnector | None = None


def get_broker_connector() -> KafkaConnector:
    """Получить глобальный экземпляр Kafka коннектора"""
    global _kafka_connector
    if _kafka_connector is None:
        _kafka_connector = KafkaConnector()
    return _kafka_connector


# Функция для graceful shutdown
def shutdown_broker():
    """Закрыть все Kafka подключения"""
    global _kafka_connector
    if _kafka_connector:
        _kafka_connector.close()
        _kafka_connector = None
