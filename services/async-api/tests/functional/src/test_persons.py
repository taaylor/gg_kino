import random
import uuid
from http import HTTPStatus
from typing import Any

import pytest
from tests.functional.core.settings import test_conf
from tests.functional.testdata.es_mapping import Mapping


@pytest.mark.asyncio
class TestPersonsAPI:

    @pytest.mark.parametrize(
        "query_data, expected_answer",
        [
            (
                {
                    "id": "4cb1cad5-7705-43c3-8c21-237e1d352c85",
                    "cached_data": True,
                },  # valid person 1
                {
                    "status": HTTPStatus.OK,
                    "length": 1,
                    "err_msg": "Ожиадалась одна валидная персона: Oleg Skorobogatko",
                },
            ),
            (
                {
                    "id": "bbbf34ad-0183-4454-8c21-c31a5579ede7",
                    "cached_data": True,
                },  # valid person 2
                {
                    "status": HTTPStatus.OK,
                    "length": 1,
                    "err_msg": "Ожиадалась одна валидная персона: Mikhail Shufutinsky",
                },
            ),
            (
                {
                    "id": "45bc4c33-4650-440d-a29c-94b2f093d3fd",
                    "cached_data": False,
                },  # unknown uuid
                {
                    "status": HTTPStatus.OK,
                    "length": 0,
                    "err_msg": "Ожидалось отсутствие персон для неизвестного UUID",
                },
            ),
            (
                {"id": "xexe", "cached_data": False},  # invalid uuid
                {
                    "status": HTTPStatus.BAD_REQUEST,
                    "length": 0,
                    "err_msg": "Ожидалась ошибка для некорректного UUID",
                },
            ),
        ],
        ids=[
            "Test valid person: Oleg Skorobogatko",
            "Test valid person: Mikhail Shufutinsky",
            "Test unknown UUID",
            "Test invalid UUID",
        ],
    )
    async def test_get_person_by_id(
        self,
        es_write_data,
        make_get_request,
        redis_test,
        query_data: dict[str, Any],
        expected_answer: dict[str, Any],
    ):
        es_data = [
            {"id": "4cb1cad5-7705-43c3-8c21-237e1d352c85", "name": "Oleg Skorobogatko"},
            {"id": "bbbf34ad-0183-4454-8c21-c31a5579ede7", "name": "Mikhail Shufutinsky"},
        ]
        await es_write_data(
            data=es_data, index=test_conf.elastic.index_persons, mapping=Mapping.persons
        )

        person_id = query_data.get("id")
        uri = f"/persons/{person_id}"

        api_body_resp, status = await make_get_request(uri)
        key_cache = f"persons:{person_id}"
        cached_person = await redis_test(key=key_cache, cached_data=query_data.get("cached_data"))

        expected_answer_status = expected_answer.get("status")
        expected_answer_lenth = expected_answer.get("length")

        assert status == expected_answer_status, expected_answer["err_msg"]

        if expected_answer_status == HTTPStatus.BAD_REQUEST:
            assert api_body_resp.get("body", True) is None, "Пустое тело ответа при ошибке"
            assert cached_person is None, "Пустой кэш при ошибке"
            return

        if not expected_answer_lenth:
            assert api_body_resp is None, "Объекты в ответе не ожидались"
            assert cached_person is None, "Кэширование не ожидалось"
            return

        for item in es_data:
            item["films"] = []
            item["full_name"] = item.pop("name")
        cached_person["id"] = cached_person.pop("uuid")
        api_body_resp["id"] = api_body_resp.pop("uuid")

        assert cached_person == api_body_resp, "Закэшированный объект не идентичен ответу API"
        assert cached_person in es_data, "Закэшированный объект не идентичен ответу БД"
        assert api_body_resp in es_data, "Ответ API не идентичен ответу БД"

    @pytest.mark.parametrize(
        "query_data, expected_answer",
        [
            (
                {"id": "bbbf34ad-0183-4454-8c21-c31a5579ede7", "cached_data": True},  # actors films
                {
                    "status": HTTPStatus.OK,
                    "length": 50,
                    "err_msg": "Ожидалось 50 фильмов для актера: Mikhail Shufutinsky",
                },
            ),
            (
                {
                    "id": "4cb1cad5-7705-43c3-8c21-237e1d352c85",
                    "cached_data": True,
                },  # directors films
                {
                    "status": HTTPStatus.OK,
                    "length": 50,
                    "err_msg": "Ожидалось 50 фильмов для режиссера: Oleg Skorobogatko",
                },
            ),
            (
                {
                    "id": "8a9f0e1f-77af-465b-abdd-339790968a26",
                    "cached_data": True,
                },  # writers films
                {
                    "status": HTTPStatus.OK,
                    "length": 50,
                    "err_msg": "Ожидалось 50 фильмов для сценариста: Michael Bay",
                },
            ),
            (
                {
                    "id": "45bc4c33-4650-440d-a29c-94b2f093d3fd",
                    "cached_data": False,
                },  # unknown uuid
                {
                    "status": HTTPStatus.OK,
                    "length": 0,
                    "err_msg": "Ожидалось отсутствие фильмов для неизвестного UUID",
                },
            ),
            (
                {"id": "xexe", "cached_data": False},  # invalid uuid
                {
                    "status": HTTPStatus.BAD_REQUEST,
                    "length": 0,
                    "err_msg": "Ожидалась ошибка для некорректного UUID",
                },
            ),
        ],
        ids=[
            "Test films for actor: Mikhail Shufutinsky",
            "Test films for director: Oleg Skorobogatko",
            "Test films for writer: Michael Bay",
            "Test unknown UUID",
            "Test invalid UUID",
        ],
    )
    async def test_get_films_for_person(
        self,
        es_write_data,
        make_get_request,
        redis_test,
        query_data: dict[str, Any],
        expected_answer: dict[str, Any],
    ):
        es_person_data = [
            {"id": "bbbf34ad-0183-4454-8c21-c31a5579ede7", "name": "Mikhail Shufutinsky"},
            {"id": "4cb1cad5-7705-43c3-8c21-237e1d352c85", "name": "Oleg Skorobogatko"},
            {"id": "8a9f0e1f-77af-465b-abdd-339790968a26", "name": "Michael Bay"},
        ]
        es_films_data = [
            {
                "id": str(uuid.uuid4()),
                "title": "Film " + str(i) + (" some horror" if i % 2 == 0 else " some triller"),
                "actors": [
                    {
                        "id": "bbbf34ad-0183-4454-8c21-c31a5579ede7",
                        "name": "Mikhail Shufutinsky",
                    }
                ],
                "directors": [
                    {
                        "id": "4cb1cad5-7705-43c3-8c21-237e1d352c85",
                        "name": "Oleg Skorobogatko",
                    }
                ],
                "writers": [{"id": "8a9f0e1f-77af-465b-abdd-339790968a26", "name": "Michael Bay"}],
                "imdb_rating": random.randrange(1, 10) + round(random.random(), 1),
                "description": "Description "
                + str(i)
                + (" about horror" if i % 2 == 0 else " about triller"),
            }
            for i in range(1, 51)
        ]
        await es_write_data(
            data=es_person_data, index=test_conf.elastic.index_persons, mapping=Mapping.persons
        )
        await es_write_data(
            data=es_films_data, index=test_conf.elastic.index_films, mapping=Mapping.films
        )

        person_id = query_data.get("id")
        uri = f"/persons/{person_id}/film"

        api_body_resp, status = await make_get_request(uri)
        key_cache = f"persons:{person_id}:films"
        cached_person_films = await redis_test(
            key=key_cache, cached_data=query_data.get("cached_data")
        )

        expected_answer_status = expected_answer.get("status")
        expected_answer_lenth = expected_answer.get("length")

        assert status == expected_answer_status, expected_answer["err_msg"]

        if expected_answer_status == HTTPStatus.BAD_REQUEST:
            assert api_body_resp.get("body", True) is None, "Пустое тело ответа при ошибке"
            assert cached_person_films is None, "Пустой кэш при ошибке"
            return

        if not expected_answer_lenth:
            assert api_body_resp == [], "Объекты в ответе не ожидались"
            assert cached_person_films is None, "Кэширование не ожидалось"
            return

        if expected_answer_lenth:
            assert (
                len(api_body_resp) == expected_answer_lenth
            ), "Кол-во объектов в ответе API не соответствует ожидаемому"
            assert (
                len(cached_person_films) == expected_answer_lenth
            ), "Кол-во объектов в кэше не соответствует ожидаемому"

        assert cached_person_films == api_body_resp, "Закэшированный объект не идентичен ответу API"


@pytest.mark.asyncio
class TestPersonSearch:
    async def prepare_persons_data(self, es_write_data, count=10):
        es_data = [
            {
                "id": str(uuid.uuid4()),
                "name": "Actor " + str(i) + (" Smith" if i % 2 == 1 else " Bond"),
            }
            for i in range(1, count + 1)
        ]
        await es_write_data(es_data, test_conf.elastic.index_persons, Mapping.persons)
        return es_data

    @pytest.mark.parametrize(
        "query_data, expected_answer",
        [
            (
                {"query": "Bond", "page_size": 0},
                {"status": HTTPStatus.BAD_REQUEST, "err_msg": "Ошибка валидации для page_size=0"},
            ),
            (
                {"query": "Bond", "page_size": 101},
                {"status": HTTPStatus.BAD_REQUEST, "err_msg": "Ошибка валидации для page_size=101"},
            ),
            (
                {"query": "Bond", "page_number": 0},
                {"status": HTTPStatus.BAD_REQUEST, "err_msg": "Ошибка валидации для page_number=0"},
            ),
        ],
        ids=[
            "Test page_size=0",
            "Test page_size=101",
            "Test page_number=0",
        ],
    )
    async def test_search_validation(
        self,
        make_get_request,
        query_data: dict[str, Any],
        expected_answer: dict[str, Any],
    ):
        _, status = await make_get_request("/persons/search", params=query_data)
        assert status == expected_answer["status"], expected_answer["err_msg"]

    @pytest.mark.parametrize(
        "query_data, expected_answer",
        [
            (
                {"query": "Bond", "page_size": 3},
                {"len_body": 3, "err_msg": "Ожидалось ровно 3 персоны с именем Bond"},
            ),
            (
                {"query": "Bond", "page_size": 1},
                {"len_body": 1, "err_msg": "Ожидалась ровно 1 персона с именем Bond"},
            ),
            (
                {"query": "Smith", "page_size": 100},
                {"len_body": 51, "err_msg": "Ожидалось 50 персон с именем Smith"},
            ),
        ],
        ids=[
            "Test page_size=3",
            "Test page_size=1",
            "Test page_size=100",
        ],
    )
    async def test_search_limit_results(
        self,
        es_write_data,
        make_get_request,
        redis_test,
        query_data: dict[str, Any],
        expected_answer: dict[str, Any],
    ):
        await self.prepare_persons_data(es_write_data, count=101)

        body, status = await make_get_request("/persons/search", params=query_data)
        key_cache = f"persons:{query_data['query']}:{query_data.get('page_number', 1)}:{query_data['page_size']}"  # noqa: E501
        cached_persons = await redis_test(key=key_cache, cached_data=True)

        assert status == HTTPStatus.OK
        assert len(body) == expected_answer["len_body"], expected_answer["err_msg"]
        assert cached_persons == body, "Закэшированный ответ не совпадает с ответом API"

    @pytest.mark.parametrize(
        "query_data, cached_data, expected_answer",
        [
            (
                {"query": "Bond", "page_size": 100},
                {"cached_data": True},
                {
                    "len_body": 50,
                    "err_msg_len_body": "Ожидалось 50 персон с именем Bond",
                    "err_msg_wrong_result": "Все имена должны содержать 'Bond'",
                },
            ),
            (
                {"query": "Smith", "page_size": 70},
                {"cached_data": True},
                {
                    "len_body": 51,
                    "err_msg_len_body": "Ожидалось 51 персона с именем Smith",
                    "err_msg_wrong_result": "Все имена должны содержать 'Smith'",
                },
            ),
            (
                {"query": "unknown", "page_size": 10},
                {"cached_data": False},
                {
                    "len_body": 0,
                    "err_msg_len_body": "Ожидался пустой результат для 'unknown'",
                    "err_msg_wrong_result": "Не должно быть результатов поиска",
                },
            ),
            (
                {"query": "Bon", "page_size": 50},
                {"cached_data": True},
                {
                    "len_body": 50,
                    "err_msg_len_body": "Ожидалось 50 персон с частью имени 'Bon'",
                    "err_msg_wrong_result": "Все имена должны содержать 'Bon'",
                },
            ),
        ],
        ids=[
            "Test query='Bond'",
            "Test query='Smith'",
            "Test query='unknown'",
            "Test partial_match='Bon'",
        ],
    )
    async def test_search_by_name(
        self,
        es_write_data,
        make_get_request,
        redis_test,
        query_data: dict[str, Any],
        cached_data: dict[str, Any],
        expected_answer: dict[str, Any],
    ):
        await self.prepare_persons_data(es_write_data, count=101)

        api_body_resp, status = await make_get_request("/persons/search", params=query_data)
        key_cache = f"persons:{query_data['query']}:{query_data.get('page_number', 1)}:{query_data['page_size']}"  # noqa: E501
        cached_persons = await redis_test(key=key_cache, cached_data=cached_data.get("cached_data"))

        assert status == HTTPStatus.OK
        assert len(api_body_resp) == expected_answer["len_body"], expected_answer[
            "err_msg_len_body"
        ]

        if api_body_resp:
            names = {person["full_name"] for person in api_body_resp}
            assert all(query_data["query"] in name for name in names), expected_answer[
                "err_msg_wrong_result"
            ]

            assert all(
                isinstance(person.get("films"), list) for person in api_body_resp
            ), "Каждая персона должна иметь список фильмов"

        if not expected_answer.get("len_body"):
            assert api_body_resp == [], "Объекты в ответе не ожидались"
            assert cached_persons is None, "Кэширование не ожидалось"
            return

        assert cached_persons == api_body_resp, "Закэшированный ответ не совпадает с ответом API"
