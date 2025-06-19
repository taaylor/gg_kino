from enum import StrEnum
from http import HTTPStatus
from typing import Any

import pytest
from tests.functional.core.settings import test_conf


class Methods(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@pytest.mark.asyncio
class TestReview:

    @pytest.mark.parametrize(
        "method, path, path_params, body_params, query_params",
        [
            (
                Methods.GET,
                "/reviews/film/{film_id}",
                {"film_id": "3e5351d6-4e4a-486b-8529-977672177a07"},
                {},
                {"page_number": 1, "page_size": 10},
            ),
            (
                Methods.GET,
                "/reviews/user",
                {},
                {},
                {"page_number": 1, "page_size": 10},
            ),
            (
                Methods.POST,
                "/reviews/{film_id}",
                {"film_id": "3e5351d6-4e4a-486b-8529-977672177a07"},
                {"text": "Отличный фильм, рекомендую к просмотру!"},
                {},
            ),
        ],
        ids=[
            "Test resp 200 ok: GET /content-api/api/v1/reviews/film/{film_id}",
            "Test resp 200 ok: GET /content-api/api/v1/reviews/user",
            "Test resp 200 ok: POST /content-api/api/v1/reviews/{film_id}",
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
        query_params: dict[str, Any],
    ):

        tokens_auth = await create_user()
        headers = {"Authorization": f'Bearer {tokens_auth.get("access_token")}'}
        enriched_path = path.format(**path_params)
        url = test_conf.contentapi.host_service + enriched_path

        if method == Methods.GET:
            body, status = await make_get_request(url=url, headers=headers, params=query_params)
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

    @pytest.mark.parametrize(
        "text, expected_status",
        [
            ("Отличный фильм!", HTTPStatus.OK),
            ("Очень интересный и захватывающий фильм с отличным сюжетом", HTTPStatus.OK),
            ("Нет", HTTPStatus.BAD_REQUEST),
            ("A" * 501, HTTPStatus.BAD_REQUEST),
        ],
        ids=[
            "Valid short review",
            "Valid long review",
            "Invalid - too short",
            "Invalid - too long",
        ],
    )
    async def test_review_text_validation(
        self,
        make_post_request,
        create_user,
        text: str,
        expected_status: HTTPStatus,
    ):
        """Тест валидации текста рецензии - должен быть от 5 до 500 символов"""
        tokens_auth = await create_user()
        headers = {"Authorization": f'Bearer {tokens_auth.get("access_token")}'}

        film_id = "3e5351d6-4e4a-486b-8529-977672177a07"
        url = f"{test_conf.contentapi.host_service}/reviews/{film_id}"
        body_params = {"text": text}

        body, status = await make_post_request(url=url, data=body_params, headers=headers)
        assert status == expected_status

    async def test_get_film_reviews_without_auth(
        self,
        make_get_request,
    ):
        """Тест получения рецензий фильма без авторизации"""
        film_id = "3e5351d6-4e4a-486b-8529-977672177a07"
        url = f"{test_conf.contentapi.host_service}/reviews/film/{film_id}"

        body, status = await make_get_request(url=url)
        assert status == HTTPStatus.OK
