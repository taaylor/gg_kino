import logging

from schemas import MessageModel

logger = logging.getLogger(__name__)


def transform_messages(messages: list[dict]) -> list[tuple]:
    """
    Преобразует сообщения из Kafka в формат для ClickHouse.

    :param messages: Список словарей с данными сообщений.
    :return: Список кортежей для вставки в ClickHouse.
    """
    transformed_messages = []

    for msg in messages:
        try:
            # Валидация через Pydantic
            validated_msg = MessageModel(**msg)

            # Преобразование в кортеж для ClickHouse
            row = (
                validated_msg.id,
                validated_msg.user_session,
                validated_msg.user_uuid,
                validated_msg.ip_address,
                validated_msg.film_uuid,
                validated_msg.event_params,
                validated_msg.event_type,
                validated_msg.message_event,
                validated_msg.event_timestamp,
                validated_msg.user_timestamp,
            )
            transformed_messages.append(row)
        except Exception as e:
            logger.error(f"Ошибка при валидации/преобразовании сообщения: {e}")
            continue

    return transformed_messages
