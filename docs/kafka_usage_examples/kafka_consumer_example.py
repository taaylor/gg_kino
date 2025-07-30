"""
Пример использования улучшенного Kafka консюмера.
"""

import asyncio
import json
import logging
from typing import Any

from utils.aiokafka_conn import MessageHandler, create_consumer

logger = logging.getLogger(__name__)


class RecsProfileMessageHandler:
    """Обработчик сообщений для recs-profile сервиса."""

    async def __call__(self, topic: str, message: bytes) -> None:
        """Обработать сообщение из Kafka."""
        try:
            # Десериализуем JSON
            data = json.loads(message.decode("utf-8"))

            logger.info(f"Получено сообщение из топика {topic}: {data}")

            # Обрабатываем в зависимости от топика
            if "bookmarks" in topic:
                await self._handle_bookmark_event(data)
            elif "ratings" in topic:
                await self._handle_rating_event(data)
            else:
                logger.warning(f"Неизвестный топик: {topic}")

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка десериализации JSON: {e}")
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}", exc_info=True)
            # Здесь можно добавить повторную отправку в DLQ

    async def _handle_bookmark_event(self, data: dict[str, Any]) -> None:
        """Обработать событие добавления в закладки."""
        user_id = data.get("user_id")
        film_id = data.get("film_id")

        logger.info(f"Пользователь {user_id} добавил фильм {film_id} в закладки")

        # Здесь ваша бизнес-логика:
        # - Обновление профиля пользователя
        # - Пересчет рекомендаций
        # - Обновление ML модели

    async def _handle_rating_event(self, data: dict[str, Any]) -> None:
        """Обработать событие оценки фильма."""
        user_id = data.get("user_id")
        film_id = data.get("film_id")
        rating = data.get("rating")

        logger.info(f"Пользователь {user_id} оценил фильм {film_id} на {rating}")

        # Здесь ваша бизнес-логика для рейтингов


async def run_consumer():
    """Запустить консюмер Kafka."""
    message_handler = RecsProfileMessageHandler()
    consumer = create_consumer()

    # Использование контекстного менеджера (рекомендуемый способ)
    async with consumer.consumer_context():
        logger.info("Консюмер запущен, ожидание сообщений...")
        await consumer.consume_messages(message_handler)


async def run_consumer_manual():
    """Ручное управление жизненным циклом консюмера."""
    message_handler = RecsProfileMessageHandler()
    consumer = create_consumer()

    try:
        await consumer.start()
        logger.info("Консюмер запущен, ожидание сообщений...")
        await consumer.consume_messages(message_handler)
    finally:
        await consumer.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Запуск консюмера с graceful shutdown
    try:
        asyncio.run(run_consumer())
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
