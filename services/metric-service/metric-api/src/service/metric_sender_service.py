import logging
import uuid
from datetime import datetime, timezone
from functools import lru_cache

import jwt
from core.config import app_config
from models.enums import EventTypes
from models.logic_models import EntryEvent, MetricEvent
from utils.kafka_connector import KafkaConnector, get_broker_connector

logger = logging.getLogger(__name__)


class MetricProcessor:
    __slots__ = "broker"

    def __init__(self, broker: KafkaConnector) -> None:
        self.broker = broker

    def take_event(self, event: EntryEvent, headers: dict) -> None:
        target_topic = None
        session_data = self._get_session_data(headers=headers)

        if event.event_type == EventTypes.LIKE:
            target_topic = app_config.kafka.like_topic
        elif event.event_type == EventTypes.COMMENT:
            target_topic = app_config.kafka.comment_topic
        elif event.event_type == EventTypes.WATCH_PROGRESS:
            target_topic = app_config.kafka.watch_progress_topic
        elif event.event_type == EventTypes.WATCH_LIST:
            target_topic = app_config.kafka.watch_list_topic
        else:
            target_topic = app_config.kafka.other_topic

        message = MetricEvent(
            id=str(uuid.uuid4()),
            user_session=session_data.get("user_session"),
            user_uuid=session_data.get("user_uuid"),
            ip_address=session_data.get("ip_address"),
            user_agent=session_data.get("user_agent"),
            film_uuid=str(getattr(event, "film_uuid", None)),
            event_type=getattr(event, "event_type", "other"),
            message_event=getattr(event, "message_event", None),
            event_params=getattr(event, "event_params", {}),
            event_timestamp=datetime.now(timezone.utc),
            user_timestamp=getattr(event, "user_timestamp", None),
        )

        logger.debug(f"Собран Event для отправки в Kafka: {message.model_dump_json(indent=4)}")

        self._send_event(topic=target_topic, message=message)

    def _send_event(self, topic: str, message: MetricEvent):

        if self.broker.send_message(topic=topic, value=message.model_dump_json()):
            logger.info(f"Сообщение: {message.id} успешно отправлено в брокер")
        else:
            logger.error(f"Сообщение {message.id} не было отправлено в брокер")

    def _get_session_data(self, headers: dict) -> dict[str, str | None]:
        token_payload = {}
        jwt_token = self._get_header_case_insensitive(headers, "Authorization")

        if jwt_token:
            _, token = jwt_token.split()
            token_payload = jwt.decode(token, options={"verify_signature": False})

            logger.debug(f"Получена сигнатура JWT токена: {token_payload}")

        return {
            "ip_address": self._get_header_case_insensitive(headers, "X-Forwarded-For"),
            "user_agent": self._get_header_case_insensitive(headers, "user-agent"),
            "user_uuid": token_payload.get("user_id"),
            "user_session": token_payload.get("session_id"),
        }

    def _get_header_case_insensitive(self, headers: dict, header_name: str) -> str | None:
        """Получить заголовок независимо от регистра"""
        for key, value in headers.items():
            if key.lower() == header_name.lower():
                return value
        return None


@lru_cache()
def get_metric_processor() -> MetricProcessor:
    broker = get_broker_connector()
    return MetricProcessor(broker)
