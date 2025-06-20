from http import HTTPStatus
from typing import Any

import pytest
from tests.functional.core.settings import test_conf
from tests.functional.testdata.model_enum import Methods


@pytest.mark.asyncio
class TestBookmarks:

    @pytest.mark.parametrize(
        "method, path, path_params, body_params",
        [
            (Methods.GET, "/bookmarks/watchlist", {}, {}),
            (
                Methods.POST,
                "/bookmarks/{film_id}",
                {"film_id": "3e5351d6-4e4a-486b-8529-977672177a07"},
                {"comment": "Звучит хайпово, посмотрю на НГ"},
            ),
            (
                Methods.PUT,
                "/bookmarks/watch-status/{film_id}",
                {"film_id": "3e5351d6-4e4a-486b-8529-977672177a07"},
                {"status": "WATCHED", "comment": "Посмотрю на НГ"},
            ),
            (
                Methods.DELETE,
                "/bookmarks/{film_id}",
                {"film_id": "3e5351d6-4e4a-486b-8529-977672177a07"},
                {},
            ),
        ],
        ids=[
            "Test resp 200 ok: GET /content-api/api/v1/bookmarks/watchlist",
            "Test resp 201 ok: POST /content-api/api/v1/bookmarks/{film_id}",
            "Test resp 200 ok: PUT /content-api/api/v1/bookmarks/watch-status/{film_id}",
            "Test resp 200 ok: DELETE /content-api/api/v1/bookmarks/{film_id}",
        ],
    )
    async def test_endpoints_express(
        self,
        make_get_request,
        make_post_request,
        make_put_request,
        make_delete_request,
        create_user,
        method: Methods,
        path: str,
        path_params: dict[str, Any],
        body_params: dict[str, Any],
    ):

        tokens_auth = await create_user()
        headers = {"Authorization": f'Bearer {tokens_auth.get("access_token")}'}
        enriched_path = path.format(**path_params)
        url = test_conf.contentapi.host_service + enriched_path
        if method == Methods.GET:
            body, status = await make_get_request(url=url, headers=headers)
            assert status == HTTPStatus.OK

        if method == Methods.POST:
            body, status = await make_post_request(url=url, data=body_params, headers=headers)
            assert status == HTTPStatus.OK or status == HTTPStatus.CREATED

        if method == Methods.PUT:
            body, status = await make_put_request(url=url, data=body_params, headers=headers)
            assert status == HTTPStatus.OK

        if method == Methods.DELETE:
            body, status = await make_delete_request(url=url, headers=headers)
            assert status == HTTPStatus.OK or status == HTTPStatus.NO_CONTENT
