from aiohttp import web


def create_app() -> web.Application:
    app = web.Application()
    return app


if __name__ == "__main__":
    app = create_app()
    web.run_app(app, port=8080)
