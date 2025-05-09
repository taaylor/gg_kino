from fastapi import Request, status
from fastapi.responses import ORJSONResponse
from opentelemetry.baggage import set_baggage
from opentelemetry import context


async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "X-Request-Id is required"}
        )

    # Создаем новый контекст с baggage
    ctx = set_baggage("request_id", request_id)
    ctx = set_baggage("http.method", request.method, context=ctx)
    ctx = set_baggage("http.route", request.url.path, context=ctx)

    # Активируем контекст для всего запроса
    token = context.attach(ctx)
    try:
        response = await call_next(request)
        return response
    finally:
        context.detach(token)
