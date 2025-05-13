from .context import current_request
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


# middleware, который кладёт Request в ContextVar
class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = current_request.set(request)
        try:
            return await call_next(request)
        finally:
            current_request.reset(token)
