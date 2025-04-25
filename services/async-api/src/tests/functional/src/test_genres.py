import uuid
from http import HTTPStatus
from typing import Any

import pytest
from tests.functional.core.settings import test_conf
from tests.functional.testdata.es_mapping import Mapping


@pytest.mark.asyncio
class TestGenres:

    async def test_genres(self, es_write_data, make_get_request, redis_test):
        # Arrange
        es_data = [
            {
                "id": str(uuid.uuid4()),
                "name": "Genre" + str(i),
            }
            for i in range(50)
        ]
        await es_write_data(es_data, test_conf.elastic.index_genres, Mapping.genres)

        # Act
        body, status = await make_get_request("/genres")
        cache = await redis_test(key="genres:all")

        # Assert
        assert status == HTTPStatus.OK, "Ожидался статус код 200 при запросе всех жанров"
        assert len(body) == 50, f"Ожидалось в ответе 50 жанров, по факту вернулось {len(body)}"
        assert len(cache) == len(
            es_data
        ), f"Количество элементов в кеше {len(cache)} != {len(es_data)} - ожидаемому результату"

    @pytest.mark.parametrize(
        "query_data, expected_answer",
        [
            (
                {"id": "526769d7-df18-4661-9aa6-49ed24e9dfd8", "cached_data": True},
                {
                    "status": HTTPStatus.OK,
                    "length": 1,
                    "err_msg_len_body": "В ответе ожидался один жанр",
                    "err_msg_cache": "Жанр ожидался в кеше",
                },
            ),
            (
                {"id": "6a0a479b-cfec-41ac-b520-41b2b007b611", "cached_data": True},
                {
                    "status": HTTPStatus.OK,
                    "length": 1,
                    "err_msg_len_body": "В ответе ожидался один жанр",
                    "err_msg_cache": "Жанр ожидался в кеше",
                },
            ),
            (
                {"id": "6a0a479b-cfec-41ac-b520-41b1b007b612", "cached_data": False},
                {
                    "status": HTTPStatus.OK,
                    "length": 0,
                    "err_msg_len_body": "В ответе ожидалось ни одного жанра",
                    "err_msg_cache": "Жанр не ожидался в кеше",
                },
            ),
            (
                {"id": "hochy_offer_v_yandex", "cached_data": False},
                {
                    "status": HTTPStatus.BAD_REQUEST,
                    "length": 0,
                    "err_msg_len_body": "В ответе ожидалось ни одного жанра",
                    "err_msg_cache": "Жанр не ожидался в кеше",
                },
            ),
        ],
        ids=[
            "Test valid genre",
            "Test valid genre",
            "Test unknow genre",
            "Test invalid uuid genre",
        ],
    )
    async def test_genres_detail(
        self,
        es_write_data,
        make_get_request,
        redis_test,
        query_data: dict[str, Any],
        expected_answer: dict[str, Any],
    ):
        # Arrange
        es_data = [
            {
                "id": "526769d7-df18-4661-9aa6-49ed24e9dfd8",
                "name": "Genre",
            },
            {
                "id": "6a0a479b-cfec-41ac-b520-41b2b007b611",
                "name": "Animation",
            },
        ]
        await es_write_data(es_data, test_conf.elastic.index_genres, Mapping.genres)
        url = "/genres/" + query_data.get("id")
        key_cache = "genres:current:" + query_data.get("id")
        expected_status = expected_answer.get("status")

        # Act
        body, status = await make_get_request(url)
        cache = await redis_test(key=key_cache, cached_data=query_data.get("cached_data"))

        # Assert
        assert status == expected_status, f"Ожидался статус код {expected_status}"

        if expected_status == HTTPStatus.BAD_REQUEST:
            assert body.get("body", True) is None, expected_answer.get("err_msg_len_body")
            assert cache is None, expected_answer.get("err_msg_cache")
            return

        if not expected_answer.get("length"):
            assert cache is None, expected_answer.get("err_msg_cache")
            assert body is None, expected_answer.get("err_msg_len_body")
            return

        cache["id"] = cache.pop("uuid")
        body["id"] = body.pop("uuid")
        assert cache in es_data, expected_answer.get("err_msg_cache")
        assert body in es_data, expected_answer.get("err_msg_len_body")
