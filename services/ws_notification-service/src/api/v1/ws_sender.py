from aiohttp import web
from storage.cache import Cache

routes = web.RouteTableDef()


@routes.get("/ws-notification/api/v1/ws-sender")
async def websocket_handler(request: web.Request) -> web.Response:
    websocket = web.WebSocketResponse()
    await websocket.prepare(request)
