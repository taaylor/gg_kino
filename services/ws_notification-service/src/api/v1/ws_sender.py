from aiohttp import web
from services.ws_service import WebSocketHandlerService

routes = web.RouteTableDef()


@routes.get("/ws-notification/api/v1/ws-sender")
async def websocket_handler(request: web.Request) -> web.Response:
    websocket_handler_service: WebSocketHandlerService = request.app.get(
        "websocket_handler_service"
    )
    if not websocket_handler_service:
        raise web.HTTPInternalServerError(reason="Ошибка сервиса, повторите попытку позже")
    return await websocket_handler_service.handle_websocket(request)
