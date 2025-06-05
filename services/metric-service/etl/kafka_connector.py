from custom_logging import get_logger
from kafka import KafkaConsumer

logger = get_logger(__name__)


class KafkaConsumerSingleton:
    _instance = None
    _consumer = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(KafkaConsumerSingleton, cls).__new__(cls)
            # Создаём KafkaConsumer с переданными параметрами
            cls._consumer = KafkaConsumer(*args, **kwargs)
            logger.info("KafkaConsumer singleton создан")
        return cls._instance

    @property
    def consumer(self):
        return self._consumer

    def close(self):
        if self._consumer:
            self._consumer.close()
            logger.info("KafkaConsumer закрыт")


# """
# messages = extract_from_kafka(
#     topics=kafka_config.topics,
#     bootstrap_servers=kafka_config.bootstrap_servers,
#     group_id=kafka_config.group_id,
#     batch_size=kafka_config.batch_size,
# )

# consumer = KafkaConsumer(
#     *topics,
#     bootstrap_servers=bootstrap_servers,
#     group_id=group_id,
#     auto_offset_reset="earliest",  # Читаем с начала для обработки всех сообщений
#     enable_auto_commit=True,
#     value_deserializer=lambda x: x.decode("utf-8"),
#     consumer_timeout_ms=5000,  # Увеличиваем общий timeout
# )
# """
# class KafkaConnector:
#     """Класс для управления подключениями к Kafka"""

#     __slots__ = ["config", "_consumer"]

#     def __init__(self) -> None:
#         self.config = self._get_config()
#         self._consumer: KafkaConsumer | None = None

#     def _get_config(self) -> dict[str, Any]:
#         return {
#             "bootstrap_servers": app_config.kafka.get_servers,
#             "client_id": app_config.project_name,
#             "value_serializer": self._json_serializer,
#             "key_serializer": lambda v: str(v).encode("utf-8") if v is not None else None,
#             "acks": app_config.kafka.acks,
#             "retries": app_config.kafka.retries,
#             "retry_backoff_ms": app_config.kafka.retry_backoff_ms,
#             "request_timeout_ms": app_config.kafka.request_timeout_ms,
#             "batch_size": app_config.kafka.batch_size,
#             "linger_ms": app_config.kafka.linger_ms,
#             "buffer_memory": app_config.kafka.buffer_memory,
#             "security_protocol": app_config.kafka.security_protocol,
#         }

#     @staticmethod
#     def _json_serializer(value: Any) -> bytes:
#         """Сериализация значений в JSON"""
#         if isinstance(value, (str, bytes)):
#             return value.encode("utf-8") if isinstance(value, str) else value
#         return json.dumps(value, ensure_ascii=False).encode("utf-8")

#     @backoff.on_exception(
#         backoff.expo,
#         (KafkaTimeoutError, KafkaConnectionError),
#         max_tries=5,
#         jitter=backoff.full_jitter,
#         max_time=60,
#     )
#     def _create_producer(self) -> KafkaConsumer:
#         try:
#             logger.debug(f"Создаю подключение к Kafka: {self.config["bootstrap_servers"]}")
#             producer = KafkaConsumer(**self.config)
#             logger.info("Kafka producer успешно создан")
#             return producer
#         except Exception as e:
#             logger.error(f"Ошибка создания Kafka producer: {e}")
#             raise

#     def get_producer(self) -> KafkaConsumer:
#         """Получить Kafka producer (singleton)"""
#         if self._consumer is None:
#             self._consumer = self._create_producer()
#         return self._consumer

#     def close(self):
#         """Закрыть подключение к Kafka"""
#         if self._consumer:
#             try:
#                 self._consumer.flush()
#                 self._consumer.close()
#                 logger.info("Kafka producer закрыт")
#             except Exception as e:
#                 logger.error(f"Ошибка при закрытии Kafka producer: {e}")
#             finally:
#                 self._consumer = None

#     @contextmanager
#     def producer_context(self):
#         """Контекстный менеджер для работы с producer"""
#         producer = None
#         try:
#             producer = self.get_producer()
#             yield producer
#         finally:
#             if producer:
#                 try:
#                     producer.flush()
#                 except Exception as e:
#                     logger.error(f"Ошибка при flush Kafka producer: {e}")

#     def send_message(
#         self,
#         topic: str,
#         value: Any,
#         key: str | bytes | None = None,
#         partition: int | None = None,
#         timestamp_ms: int | None = None,
#         headers: str | bytes | None = None,
#     ) -> bool:
#         """
#         Отправить сообщение в Kafka

#         Returns:
#             bool: True если сообщение отправлено успешно
#         """
#         try:
#             with self.producer_context() as producer:
#                 message = producer.send(
#                     topic=topic,
#                     value=value,
#                     key=key,
#                     partition=partition,
#                     timestamp_ms=timestamp_ms,
#                     headers=headers,
#                 )

#                 record_metadata = message.get(timeout=10)
#                 logger.debug(
#                     f"Сообщение отправлено в топик {record_metadata.topic}, partition {record_metadata.partition}, offset {record_metadata.offset}"  # noqa E501
#                 )
#                 return True

#         except KafkaTimeoutError:
#             logger.error(f"Таймаут при отправке сообщения в топик {topic}")
#             return False
#         except KafkaError as e:
#             logger.error(f"Ошибка Kafka при отправке в топик {topic}: {e}")
#             return False
#         except Exception as e:
#             logger.error(f"Неожиданная ошибка при отправке в топик {topic}: {e}")
#             return False

#     def __enter__(self):
#         return self

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.close()
