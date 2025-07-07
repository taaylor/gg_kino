import json
import logging
from functools import lru_cache

from aiohttp import ClientConnectionError, WSCloseCode, web
from core.config import app_config
from services.base_service import BaseService
from storage.cache import Cache
from utils.ws_connections import connections

logger = logging.getLogger(__name__)


class WebSocketHandlerService(BaseService):

    async def handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """
        Обработчик WebSocket соединения для пользователей.
        :param request: HTTP запрос, содержащий информацию о соединении.
        """
        user_id = request.get("user").get("user_id")
        websocket = web.WebSocketResponse()
        await websocket.prepare(request)

        if user_id in connections:
            logger.warning(f"Пользователь {user_id} уже подключен к каналу по websocket")
            await websocket.close(code=WSCloseCode.OK, message="Пользователь уже подключен")
            return websocket

        connections[user_id] = websocket
        logger.debug(f"Пользователь {user_id=} подключился к каналу по websocket")

        try:
            await self._check_event_user(websocket, user_id)
            async for message in websocket:
                if message.type == web.WSMsgType.CLOSED:
                    break
                elif message.type == web.WSMsgType.ERROR:
                    logger.warning(f"Ошибка WebSocket для {user_id}: {websocket.exception()}")
                    break
        except ClientConnectionError as error:
            logger.warning(f"Возникло исключение с соединением пользователя: {error}")
        except Exception as error:
            logger.error(
                f"Произошла ошибка при обработке WebSocket для пользователя {user_id}: {error}"
            )
            await websocket.close()
        finally:
            connections.pop(user_id, None)
            logger.info(
                f"Пользователь {user_id} отключился, \
                    код закрытия: {websocket.close_code}."
            )
        return websocket

    async def _check_event_user(self, websocket: web.WebSocketResponse, user_id: str) -> None:
        """
        Проверяет наличие событий для пользователя.
        :param websocket: Соединение WebSocket пользователя.
        :param user_id: Идентификатор пользователя.
        """

        cursor = send_event = 0
        user_key_cache_not_send = self.__class__.key_cache_not_send_event.format(
            user_id=user_id, event_id="*"
        )

        while True:
            cursor, keys = await self.cache.scan(
                cursor=cursor, match=user_key_cache_not_send, count=100
            )
            for key in keys:
                user_event = await self.cache.get(key)
                if user_event:
                    user_event = json.loads(user_event)
                    await websocket.send_json(user_event)
                    send_event += 1
                    logger.debug(f"Отправлено событие для пользователя {user_id} из кеша.")

                    user_key_cache_send = self.__class__.key_cache_send_event.format(
                        user_id=user_id, event_id=user_event.get("id")
                    )
                    await self.cache.background_set(
                        key=user_key_cache_send,
                        value=user_event.get("id"),
                        expire=app_config.cache_expire_time,
                    )
                await self.cache.background_destroy(key)
            if cursor == 0:
                break

        logger.info(
            f"Проверка событий для пользователя {user_id} завершена. \
                Отправлено {send_event} событий из кеша."
        )
        return None


@lru_cache
def get_websocket_handler_service(cache: Cache) -> WebSocketHandlerService:
    return WebSocketHandlerService(cache)
