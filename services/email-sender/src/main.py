import asyncio
import logging
import signal

from services.processors.event_handler import EventHandler, get_event_handler
from storage.messagebroker import get_message_broker

logger = logging.getLogger(__name__)


async def main():
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    # 1) Получаем глобальный брокер
    broker = get_message_broker()

    # 2) Список очередей, которые будем слушать
    queues = [
        "auto-mailing.launched.notification.email-sender",
        "user.registered.notification.email-sender",
        "manager-mailing.launched.notification.email-sender",
    ]
    event_handler: EventHandler = get_event_handler()

    # 3) Запускаем задачи‑консьюмеры
    tasks = []
    for q in queues:
        logger.info(f"Запускаем consumer для очереди: {q}")
        tasks.append(
            asyncio.create_task(
                broker.consumer(
                    queue_name=q,
                    callback=event_handler.event_handler,
                ),
                name=f"consumer:{q}",
            )
        )
    logger.info("Все консьюмеры запущены. Ждём сообщений…")

    # 4) Ждём SIGINT/SIGTERM для graceful shutdown
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, stop_event.set)
    loop.add_signal_handler(signal.SIGTERM, stop_event.set)

    await stop_event.wait()
    logger.info("Получен сигнал остановки, завершаем работу…")

    # 5) Закрываем брокер и отменяем таски
    await broker.close()
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("Сервис корректно остановлен.")


if __name__ == "__main__":
    asyncio.run(main())
