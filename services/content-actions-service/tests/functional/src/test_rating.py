from enum import StrEnum
from http import HTTPStatus
from typing import Any

import pytest
from tests.functional.core.settings import test_conf


class Methods(StrEnum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


@pytest.mark.asyncio
class TestRating:

    @pytest.mark.parametrize(
        "method, path, path_params, body_params",
        [
            (
                Methods.GET,
                "/films-rating/{film_id}",
                {"film_id": "3e5351d6-4e4a-486b-8529-977672177a07"},
                {},
            ),
            (
                Methods.POST,
                "/films-rating/{film_id}",
                {"film_id": "3e5351d6-4e4a-486b-8529-977672177a07"},
                {"score": 8},
            ),
            (
                Methods.DELETE,
                "/films-rating/{film_id}",
                {"film_id": "3e5351d6-4e4a-486b-8529-977672177a07"},
                {},
            ),
        ],
        ids=[
            "Test resp 200 ok: GET /content-api/api/v1/films-rating/{film_id}",
            "Test resp 201 ok: POST /content-api/api/v1/films-rating/{film_id}",
            "Test resp 204 ok: DELETE /content-api/api/v1/films-rating/{film_id}",
        ],
    )
    async def test_endpoints_express(
        self,
        make_get_request,
        make_post_request,
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

        if method == Methods.DELETE:
            body, status = await make_delete_request(url=url, headers=headers)
            assert status == HTTPStatus.OK or status == HTTPStatus.NO_CONTENT

    @pytest.mark.parametrize(
        "score, expected_status",
        [
            (1, HTTPStatus.CREATED),
            (5, HTTPStatus.CREATED),
            (10, HTTPStatus.CREATED),
            (0, HTTPStatus.BAD_REQUEST),
            (11, HTTPStatus.BAD_REQUEST),
        ],
        ids=[
            "Valid score 1",
            "Valid score 5",
            "Valid score 10",
            "Invalid score 0",
            "Invalid score 11",
        ],
    )
    async def test_score_validation(
        self,
        make_post_request,
        create_user,
        score: int,
        expected_status: HTTPStatus,
    ):
        """Тест валидации оценок - должны принимать только значения от 1 до 10"""
        tokens_auth = await create_user()
        headers = {"Authorization": f'Bearer {tokens_auth.get("access_token")}'}

        film_id = "3e5351d6-4e4a-486b-8529-977672177a07"
        url = f"{test_conf.contentapi.host_service}/films-rating/{film_id}"
        body_params = {"score": score}

        body, status = await make_post_request(url=url, data=body_params, headers=headers)
        assert status == expected_status

    async def test_get_rating_without_auth(
        self,
        make_get_request,
    ):
        """Тест получения рейтинга без авторизации - должен работать с jwt_optional"""
        film_id = "3e5351d6-4e4a-486b-8529-977672177a07"
        url = f"{test_conf.contentapi.host_service}/films-rating/{film_id}"

        body, status = await make_get_request(url=url)
        # Метод get_avg_rating использует jwt_optional, поэтому должен работать без авторизации
        assert status == HTTPStatus.OK

    async def test_rating_flow(
        self,
        make_get_request,
        make_post_request,
        make_delete_request,
        create_user,
    ):
        """Тест полного флоу: поставить оценку -> получить рейтинг -> удалить оценку"""
        tokens_auth = await create_user()
        headers = {"Authorization": f'Bearer {tokens_auth.get("access_token")}'}

        film_id = "3e5351d6-4e4a-486b-8529-977672177a07"
        base_url = f"{test_conf.contentapi.host_service}/films-rating/{film_id}"

        # 1. Поставить оценку
        score_data = {"score": 7}
        body, status = await make_post_request(url=base_url, data=score_data, headers=headers)
        assert status == HTTPStatus.CREATED

        # 2. Получить рейтинг
        body, status = await make_get_request(url=base_url, headers=headers)
        assert status == HTTPStatus.OK
        assert "rating" in body
        assert "votes_count" in body

        # 3. Удалить оценку
        body, status = await make_delete_request(url=base_url, headers=headers)
        assert status == HTTPStatus.NO_CONTENT
