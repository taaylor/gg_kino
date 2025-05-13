from contextvars import ContextVar

from fastapi import Request

# создаём глобальный ContextVar
current_request: ContextVar[Request] = ContextVar("current_request")
