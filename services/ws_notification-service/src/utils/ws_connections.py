from typing import TypeAlias

from aiohttp import web

WebSocketConnections: TypeAlias = dict[str, web.WebSocketResponse]
connections: WebSocketConnections = {}
