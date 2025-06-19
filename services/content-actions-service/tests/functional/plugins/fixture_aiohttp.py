from json.decoder import JSONDecodeError

import aiohttp
import pytest_asyncio


@pytest_asyncio.fixture(scope="function")
async def aiohttp_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name="make_get_request")
async def make_get_request(aiohttp_session: aiohttp.ClientSession):
    async def inner(
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> tuple[list | dict, int]:
        async with aiohttp_session.get(url, params=params, headers=headers) as response:
            try:
                body = await response.json()
            except (JSONDecodeError, TypeError, aiohttp.ContentTypeError):
                body = []
            status = response.status
        return body, status

    return inner


@pytest_asyncio.fixture(name="make_post_request")
async def make_post_request(aiohttp_session: aiohttp.ClientSession):
    async def inner(
        url: str,
        data: dict | None = None,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> tuple[list | dict, int]:
        async with aiohttp_session.post(
            url,
            json=data,
            params=params,
            headers=headers,
        ) as response:
            try:
                body = await response.json()
            except (JSONDecodeError, TypeError, aiohttp.ContentTypeError):
                body = []
            status = response.status
        return body, status

    return inner


@pytest_asyncio.fixture(name="make_put_request")
async def make_put_request(aiohttp_session: aiohttp.ClientSession):
    async def inner(
        url: str,
        data: dict | None = None,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> tuple[list | dict, int]:
        async with aiohttp_session.put(
            url,
            json=data,
            params=params,
            headers=headers,
        ) as response:
            try:
                body = await response.json()
            except (JSONDecodeError, TypeError, aiohttp.ContentTypeError):
                body = []
            status = response.status
        return body, status

    return inner


@pytest_asyncio.fixture(name="make_delete_request")
async def make_delete_request(aiohttp_session: aiohttp.ClientSession):
    async def inner(
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> tuple[list | dict, int]:
        async with aiohttp_session.delete(
            url,
            params=params,
            headers=headers,
        ) as response:
            try:
                body = await response.json()
            except (JSONDecodeError, TypeError, aiohttp.ContentTypeError):
                body = []
            status = response.status
        return body, status

    return inner
