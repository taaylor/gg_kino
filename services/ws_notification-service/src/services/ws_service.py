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

    async def handle_websocket(  # noqa: WPS213, WPS231
        self, request: web.Request
    ) -> web.WebSocketResponse:
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

        try:  # noqa: WPS229
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
        Проверяет наличие событий для пользователя в кеше.
        :param websocket: Соединение WebSocket пользователя.
        :param user_id: Идентификатор пользователя.
        """
        send_event = 0
        key_not_send = self.__class__.key_event_not_send.format(user_id=user_id, event_id="*")
        keys = await self.cache.scan_keys(pattern=key_not_send)

        for key in keys:
            user_event = await self.cache.get(key)  # type: ignore
            if user_event:
                user_event = json.loads(user_event)  # type: ignore
                await websocket.send_json(user_event)
                send_event += 1
                logger.debug(
                    (
                        f"Отправлено событие {user_event.get("id")}"  # type: ignore
                        f"для пользователя {user_id} из кеша."
                    )
                )
                await self.cache.background_set(
                    key=self.__class__.key_event_send.format(
                        user_id=user_id, event_id=user_event.get("id")  # type: ignore
                    ),
                    value=json.dumps({"id": user_event.get("id")}),  # type: ignore
                    expire=app_config.redis.cache_expire_time,
                )
                await self.cache.background_destroy(key)

        logger.info(
            f"Проверка событий для пользователя {user_id} завершена. \
                Отправлено {send_event} событий из кеша."
        )


@lru_cache
def get_websocket_handler_service(cache: Cache) -> WebSocketHandlerService:
    return WebSocketHandlerService(cache)
