import aiohttp
import pytest_asyncio
from tests.functional.core.settings import test_conf


@pytest_asyncio.fixture(scope="session")
async def aiohttp_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name="make_get_request")
def make_get_request(aiohttp_session: aiohttp.ClientSession):

    async def inner(uri: str, params: dict | None = None) -> tuple[list, int]:

        url = test_conf.api.host_service + "/v1" + uri

        async with aiohttp_session.get(url, params=params) as response:
            body = await response.json()
            status = response.status

        return body, status

    return inner
