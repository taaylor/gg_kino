from core.logger_config import get_logger
from kafka import KafkaConsumer

logger = get_logger(__name__)


class KafkaConsumerSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = KafkaConsumer(*args, **kwargs)
        return cls._instance
