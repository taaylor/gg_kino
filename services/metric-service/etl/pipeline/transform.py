from core.logger_config import get_logger
from utils.schemas import MessageModel

logger = get_logger(__name__)


def transform_messages(messages: list[dict]) -> list[tuple]:
    """
    Преобразует сообщения из Kafka в формат для ClickHouse.

    :param messages: Список словарей с данными сообщений.
    :return: Список кортежей для вставки в ClickHouse.
    """
    transformed_messages = [None] * len(messages)

    for idx, msg in enumerate(messages, start=0):
        try:
            # Валидация через Pydantic
            validated_msg = MessageModel(
                user_session=msg["user_session"],
                user_uuid=msg["user_uuid"],
                ip_address=msg["ip_address"],
                user_agent=msg["user_agent"],
                film_uuid=msg["film_uuid"],
                event_type=msg["event_type"],
                message_event=msg["message_event"],
                event_params=msg["event_params"],
                event_timestamp=msg["event_timestamp"],
                user_timestamp=msg["user_timestamp"],
            )

            # Преобразование в кортеж для ClickHouse
            row = (
                validated_msg.user_session,
                validated_msg.user_uuid,
                validated_msg.user_agent,
                validated_msg.ip_address,
                validated_msg.film_uuid,
                validated_msg.event_params,
                validated_msg.event_type,
                validated_msg.message_event,
                validated_msg.event_timestamp,
                validated_msg.user_timestamp,
            )

            transformed_messages[idx] = row

        except Exception as e:
            logger.error(f"Ошибка при валидации/преобразовании сообщения: {e}")
            continue

    return transformed_messages
