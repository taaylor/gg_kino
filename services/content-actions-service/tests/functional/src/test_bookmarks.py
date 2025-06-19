import pytest
from tests.functional.core.settings import test_conf


class TestBookmarks:

    @pytest.mark.asyncio
    async def test_get_watchlist(
        self,
        make_get_request,
        create_user,
    ):

        tokens_auth = await create_user()
        url = test_conf.contentapi.host_service + "/bookmarks/watchlist"
        headers = {"Authorization": f'Bearer {tokens_auth.get("access_token")}'}
        body, status = await make_get_request(url=url, headers=headers)

        assert status == 200
