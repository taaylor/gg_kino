import asyncio
import json
import logging
from http import HTTPStatus

from aiohttp import ClientSession
from models.models import EventsIdsLogic
from storage.cache import Cache

logger = logging.getLogger(__name__)


class SupplierProcessor:

    key_cache_send_event = "send_event:{0}:{1}"
    key_cache_not_send_event = "not_send_event:{0}:{1}"

    __slots__ = ("cache", "client_session")

    def __init__(self, cache: Cache, client_session: ClientSession) -> None:
        self.cache = cache
        self.client_session = client_session

    async def supplier_processor(self) -> None:
        """
        Основной цикл для отправки статусов уведомлений в сервис notification.
        Периодически проверяет кеш на наличие событий, отправляет их статусы и удаляет из кеша при успехе.
        """
        logger.info("Запуск процесса отправки статуса уведомления в сервис notification")
        key_cache_send_event = self.__class__.key_cache_send_event.format("*", "*")
        key_cache_not_send_event = self.__class__.key_cache_not_send_event.format("*", "*")
        while True:
            try:
                keys_event_send, keys_event_not_send = await asyncio.gather(
                    self.cache.scan_keys(key_cache_send_event),
                    self.cache.scan_keys(key_cache_not_send_event),
                )
                ids_event_send, ids_event_not_send = await asyncio.gather(
                    self._get_ids_events(keys_event_send), self._get_ids_events(keys_event_not_send)
                )

                if not ids_event_send and not ids_event_not_send:
                    logger.info("Событий в кеше не найдено, перехожу в режим ожидания")
                    await asyncio.sleep(10)
                    continue

                request_body = EventsIdsLogic(
                    sent_success=ids_event_send, failure=ids_event_not_send
                ).model_dump(mode="json")

                # TODO: добавить url, api-key
                async with self.client_session.post(
                    url=..., data=request_body, timeout=10, headers=None
                ) as response:
                    if response.ok:
                        await self.cache.destroy(*keys_event_send)
                        logger.info(
                            f"Данные успешно отправлены в сервис нотификации и удалены из кеша \
                                (отправленных {len(keys_event_send)}, не отправленных {len(keys_event_not_send)})"
                        )
                    else:
                        logger.error(f"Сервис notification недоступен, статус: {response.status}")
            except Exception as error:
                logger.error(
                    f"Ошибка в процессе отправки статуса уведомления в сервис notification: {error}"
                )
                await asyncio.sleep(10)  # делаем паузу перед повторной попыткой
            await asyncio.sleep(10)

    async def _get_ids_events(self, keys: list[str]) -> list[str]:
        """
        Получает ID событий из кеша по заданным ключам.
        :param keys: Список ключей в кеше.
        :return: Список ID событий.
        """

        if not keys:
            return []

        tasks = (asyncio.create_task(self.cache.get(key)) for key in keys)
        events = await asyncio.gather(*tasks)
        ids = [event.get("id") for event in events if event]
        return ids


def get_supplier_processor(cache: Cache, client_session: ClientSession) -> SupplierProcessor:

    return SupplierProcessor(cache=cache, client_session=client_session)
