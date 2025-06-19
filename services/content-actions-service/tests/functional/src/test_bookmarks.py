from enum import StrEnum
from http import HTTPStatus
from typing import Any

import pytest
from tests.functional.core.settings import test_conf


class Methods(StrEnum):
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    DELETE = "DELETE"

    # test_films: set[UUID] = {
    #     UUID("3e5351d6-4e4a-486b-8529-977672177a07"),
    #     UUID("a88cbbeb-b998-4ca6-aeff-501463dcdaa0"),
    #     UUID("7f28af8a-c629-4af0-b87b-39368a5b8464"),
    #     UUID("ee1baa06-a221-4d8c-8678-992e8e84c5c1"),
    #     UUID("e5a21648-59b1-4672-ac3b-867bcd64b6ea"),
    #     UUID("f061235e-779f-4a59-9eaa-fc533c3c0584"),
    #     UUID("b16d59f7-a386-467b-bea3-35e7ffbba902"),
    #     UUID("53d660a1-be2b-4b53-9761-0a315a693789"),
    #     UUID("0312ed51-8833-413f-bff5-0e139c11264a"),
    #     UUID("991d143e-1342-4f7c-abf0-a9ede3abba20"),
    #     UUID("248041f8-8c65-4539-b684-e8f4cd01d10f"),
    #     UUID("db594b91-a587-48c4-bac9-5c6be5e4cf33"),
    #     UUID("f553752e-71c7-4ea0-b780-41408516d0f4"),
    #     UUID("00e2e781-7af9-4f82-b4e9-14a488a3e184"),
    #     UUID("aa5aea7a-cd65-4aec-963f-98375b370717"),
    # }


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
