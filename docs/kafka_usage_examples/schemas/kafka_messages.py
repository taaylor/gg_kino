"""
Схемы сообщений Kafka для recs-profile сервиса.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID


@dataclass
class BaseKafkaMessage:
    """Базовый класс для всех Kafka сообщений."""

    timestamp: datetime
    user_id: UUID
    event_id: Optional[str] = None

    @classmethod
    def from_bytes(cls, data: bytes) -> "BaseKafkaMessage":
        """Создать объект из bytes."""
        try:
            json_data = json.loads(data.decode("utf-8"))
            return cls.from_dict(json_data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Ошибка парсинга сообщения: {e}") from e

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseKafkaMessage":
        """Создать объект из словаря."""
        # Конвертируем timestamp
        timestamp_str = data.get("timestamp")
        if isinstance(timestamp_str, str):
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        else:
            timestamp = datetime.now()

        # Конвертируем user_id
        user_id_str = data.get("user_id")
        if isinstance(user_id_str, str):
            user_id = UUID(user_id_str)
        else:
            raise ValueError("user_id обязателен и должен быть UUID")

        return cls(timestamp=timestamp, user_id=user_id, event_id=data.get("event_id"))

    def to_dict(self) -> Dict[str, Any]:
        """Конвертировать в словарь."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "user_id": str(self.user_id),
            "event_id": self.event_id,
        }


@dataclass
class BookmarkEventMessage(BaseKafkaMessage):
    """Сообщение о добавлении фильма в закладки."""

    film_id: UUID
    action: str  # 'add' or 'remove'

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BookmarkEventMessage":
        """Создать объект из словаря."""
        base = super().from_dict(data)

        film_id_str = data.get("film_id")
        if isinstance(film_id_str, str):
            film_id = UUID(film_id_str)
        else:
            raise ValueError("film_id обязателен и должен быть UUID")

        action = data.get("action", "add")
        if action not in ["add", "remove"]:
            raise ValueError("action должен быть 'add' или 'remove'")

        return cls(
            timestamp=base.timestamp,
            user_id=base.user_id,
            event_id=base.event_id,
            film_id=film_id,
            action=action,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Конвертировать в словарь."""
        result = super().to_dict()
        result.update({"film_id": str(self.film_id), "action": self.action})
        return result


@dataclass
class RatingEventMessage(BaseKafkaMessage):
    """Сообщение о рейтинге фильма пользователем."""

    film_id: UUID
    rating: float
    previous_rating: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RatingEventMessage":
        """Создать объект из словаря."""
        base = super().from_dict(data)

        film_id_str = data.get("film_id")
        if isinstance(film_id_str, str):
            film_id = UUID(film_id_str)
        else:
            raise ValueError("film_id обязателен и должен быть UUID")

        rating = data.get("rating")
        if rating is None or not isinstance(rating, (int, float)):
            raise ValueError("rating обязателен и должен быть числом")

        if not (0.0 <= rating <= 10.0):
            raise ValueError("rating должен быть от 0 до 10")

        previous_rating = data.get("previous_rating")
        if previous_rating is not None:
            if not isinstance(previous_rating, (int, float)) or not (
                0.0 <= previous_rating <= 10.0
            ):
                raise ValueError("previous_rating должен быть от 0 до 10")

        return cls(
            timestamp=base.timestamp,
            user_id=base.user_id,
            event_id=base.event_id,
            film_id=film_id,
            rating=float(rating),
            previous_rating=float(previous_rating) if previous_rating is not None else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Конвертировать в словарь."""
        result = super().to_dict()
        result.update(
            {
                "film_id": str(self.film_id),
                "rating": self.rating,
                "previous_rating": self.previous_rating,
            }
        )
        return result


class MessageParser:
    """Парсер для Kafka сообщений."""

    MESSAGE_TYPES = {
        "bookmark": BookmarkEventMessage,
        "rating": RatingEventMessage,
    }

    @classmethod
    def parse_message(cls, topic: str, data: bytes) -> BaseKafkaMessage:
        """Парсить сообщение в зависимости от топика."""
        try:
            # Определяем тип сообщения по топику
            message_type = cls._get_message_type_from_topic(topic)

            if message_type:
                return message_type.from_bytes(data)
            else:
                # Парсим как базовое сообщение, если тип неопределен
                return BaseKafkaMessage.from_bytes(data)

        except Exception as e:
            raise ValueError(f"Ошибка парсинга сообщения из топика {topic}: {e}") from e

    @classmethod
    def _get_message_type_from_topic(cls, topic: str) -> Optional[type]:
        """Определить тип сообщения по топику."""
        if "bookmark" in topic.lower():
            return BookmarkEventMessage
        elif "rating" in topic.lower():
            return RatingEventMessage
        else:
            return None


# Типизированный обработчик сообщений
async def typed_message_handler(topic: str, message: bytes) -> None:
    """Типизированный обработчик сообщений."""
    try:
        # Парсим сообщение в типизированный объект
        parsed_message = MessageParser.parse_message(topic, message)

        # Обрабатываем в зависимости от типа
        if isinstance(parsed_message, BookmarkEventMessage):
            await handle_bookmark_event(parsed_message)
        elif isinstance(parsed_message, RatingEventMessage):
            await handle_rating_event(parsed_message)
        else:
            await handle_generic_event(parsed_message)

    except ValueError as e:
        # Логируем ошибку парсинга, но не прерываем обработку
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка парсинга сообщения из {topic}: {e}")


async def handle_bookmark_event(message: BookmarkEventMessage) -> None:
    """Обработать событие добавления/удаления закладки."""
    import logging

    logger = logging.getLogger(__name__)

    logger.info(
        f"Пользователь {message.user_id} {message.action} фильм {message.film_id} "
        f"{'в закладки' if message.action == 'add' else 'из закладок'}"
    )

    # Здесь ваша бизнес-логика:
    # - Обновление профиля пользователя
    # - Пересчет рекомендаций на основе жанров/актеров фильма
    # - Обновление модели коллаборативной фильтрации


async def handle_rating_event(message: RatingEventMessage) -> None:
    """Обработать событие оценки фильма."""
    import logging

    logger = logging.getLogger(__name__)

    logger.info(
        f"Пользователь {message.user_id} оценил фильм {message.film_id} "
        f"на {message.rating}"
        + (f" (было {message.previous_rating})" if message.previous_rating else "")
    )

    # Здесь ваша бизнес-логика:
    # - Обновление матрицы пользователь-фильм для collaborative filtering
    # - Обновление профиля предпочтений пользователя
    # - Пересчет похожих пользователей


async def handle_generic_event(message: BaseKafkaMessage) -> None:
    """Обработать общее событие."""
    import logging

    logger = logging.getLogger(__name__)

    logger.info(f"Получено общее событие от пользователя {message.user_id}")
