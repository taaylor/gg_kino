from aiohttp import web
from api.v1 import ws_sender
from middleware.middleware import authorize_middleware
from utils.connectors import cleanup_dependencies, setup_dependencies


def start_application() -> web.Application:
    """
    Фабрика инициализации приложения
    """
    app = web.Application()
    app.add_routes(ws_sender.routes)
    app.on_startup.append(setup_dependencies)
    app.on_cleanup.append(cleanup_dependencies)
    app.middlewares.append(authorize_middleware)
    return app


app = start_application()
