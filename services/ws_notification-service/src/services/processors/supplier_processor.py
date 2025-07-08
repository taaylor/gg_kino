import asyncio
import json
import logging

from aiohttp import ClientSession
from core.config import app_config
from models.models import EventsIdsLogic
from services.base_service import BaseService
from storage.cache import Cache

logger = logging.getLogger(__name__)


LIMIT_KEYS = 500


class SupplierProcessor(BaseService):

    def __init__(self, cache: Cache, client_session: ClientSession) -> None:
        super().__init__(cache=cache)
        self.client_session = client_session
        self.callback_url = app_config.notification_api.get_url
        self.headers = {"X-Api-Key": app_config.api_keys[0], "Content-Type": "application/json"}

    async def supplier_processor(self) -> None:  # noqa: WPS217, WPS210, WPS213, WPS231
        """
        Основной цикл для отправки статусов уведомлений в сервис notification.
        Периодически проверяет кеш на наличие событий, отправляет их статусы
        и удаляет из кеша при успехе.
        """

        logger.debug("Запуск процесса отправки статуса уведомления в сервис notification")
        key_send_event = self.__class__.key_event_send.format(user_id="*", event_id="*")
        key_fail_event = self.__class__.key_event_fail.format(user_id="*", event_id="*")

        while True:
            try:  # noqa: WPS229
                keys_send_event, keys_fail_event = await asyncio.gather(
                    self.cache.scan_keys(pattern=key_send_event, count=LIMIT_KEYS),
                    self.cache.scan_keys(pattern=key_fail_event, count=LIMIT_KEYS),
                )

                ids_event_send, ids_event_fail = await asyncio.gather(
                    self._get_ids_events(keys_send_event), self._get_ids_events(keys_fail_event)
                )

                if not ids_event_send and not ids_event_fail:
                    logger.info("Событий в кеше не найдено, перехожу в режим ожидания")
                    continue

                logger.info(
                    f"Найдено ids событий отправленных {len(ids_event_send)}, \
                        не отправленных {len(ids_event_fail)} в кеше"
                )

                # для избежания багов и тд. исключаем из множества не успешных событий, успешные.
                # чтобы избежать дублирования идентификаторов, в двух очередях
                ids_event_fail.difference_update(ids_event_send)

                request_body = EventsIdsLogic(
                    sent_success=list(ids_event_send), failure=list(ids_event_fail)
                ).model_dump(mode="json")

                logger.info(f"Делаю запрос в сервис нотификации с телом {request_body}")

                async with self.client_session.post(
                    url=self.callback_url,
                    json=request_body,
                    timeout=5,
                    headers=self.headers,
                ) as response:
                    if response.ok:
                        await self.cache.destroy(*keys_send_event, *keys_fail_event)
                        logger.info(
                            f"Данные успешно отправлены в сервис нотификации и удалены из кеша \
                                (отправленных {len(keys_send_event)}, \
                                    не отправленных {len(keys_fail_event)})"
                        )
                    else:
                        logger.error(
                            f"Сервис notification недоступен, статус: {response.status}, {response}"
                        )
            except Exception as error:
                logger.error(
                    f"Ошибка в процессе отправки статуса уведомления в сервис notification: {error}"
                )
            finally:
                await asyncio.sleep(10)

    async def _get_ids_events(self, keys: list[str]) -> set[str]:
        """
        Получает ID событий из кеша по заданным ключам.
        :param keys: Список ключей в кеше.
        :return: Список ID событий.
        """

        if not keys:
            return set()

        # используем магию asyncio для получения кеша
        tasks = (asyncio.create_task(self.cache.get(key)) for key in keys)
        events = await asyncio.gather(*tasks)
        ids = set(json.loads(event).get("id") for event in events if event)  # noqa: WPS221
        return ids


def get_supplier_processor(cache: Cache, client_session: ClientSession) -> SupplierProcessor:
    return SupplierProcessor(cache=cache, client_session=client_session)
