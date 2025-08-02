import logging
from http import HTTPMethod
from typing import Any, Callable, Coroutine

import httpx
import pytest_asyncio

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture(name="make_request")
async def make_request() -> Callable[..., Coroutine[Any, Any, tuple[int, dict[str, Any] | None]]]:
    async def inner(
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        method: HTTPMethod = HTTPMethod.GET,
    ) -> tuple[int, dict[str, Any] | None]:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30)) as client:
            try:
                match method:
                    case HTTPMethod.GET:
                        response = await client.get(url, params=params, headers=headers)
                    case HTTPMethod.POST:
                        response = await client.post(url, params=params, headers=headers, json=data)
                    case _:
                        raise ValueError(f"Недоступен вызов метода{method}")

                body = response.json()

            except httpx.RequestError as e:
                logger.error(f"Ошибка при выполнении {method} запроса на {url}.", exc_info=True)
                return 0, {"error": str(e)}
            except Exception as e:
                logger.error(
                    f"Неожиданная ошибка при выполнении {method} запроса на {url}.", exc_info=True
                )
                return 0, {"error": str(e)}
            return response.status_code, body

    return inner
