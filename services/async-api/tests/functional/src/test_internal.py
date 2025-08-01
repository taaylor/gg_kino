import random
from http import HTTPStatus
from pprint import pprint as pp

import pytest
from tests.functional.core.settings import test_conf
from tests.functional.testdata.es_mapping import Mapping


@pytest.mark.asyncio
class TestFilmsSearchByVector:

    def prepare_uuids_and_vectors(self):
        film_uuids_for_near_embedding = [
            "3d825f60-9fff-4dfe-b294-1a45fa1e115d",
            "0312ed51-8833-413f-bff5-0e139c11264a",
            "025c58cd-1b7e-43be-9ffb-8571a613579b",
            "cddf9b8f-27f9-4fe9-97cb-9e27d4fe3394",
            "3b914679-1f5e-4cbd-8044-d13d35d5236c",
            "516f91da-bd70-4351-ba6d-25e16b7713b7",
            "c4c5e3de-c0c9-4091-b242-ceb331004dfd",
            "4af6c9c9-0be0-4864-b1e9-7f87dd59ee1f",
            "12a8279d-d851-4eb9-9d64-d690455277cc",
            "118fd71b-93cd-4de5-95a4-e1485edad30e",
        ]
        film_uuids_for_far_embedding = [
            "46f15353-2add-415d-9782-fa9c5b8083d5",
            "db5dcded-29da-4c96-91a2-df1407f0a80a",
            "fda827f8-d261-4c23-9e9c-e42787580c4d",
            "57beb3fd-b1c9-4f8a-9c06-2da13f95251c",
            "b1f1e8a6-e310-47d9-a93c-6a7b192bac0e",
            "50fb4de9-e4b3-4aca-9f2f-00a48f12f9b3",
            "6e5cd268-8ce4-45f9-87d2-52f0f26edc9e",
            "b1384a92-f7fe-476b-b90b-6cec2b7a0dce",
            "c9e1f6f0-4f1e-4a76-92ee-76c1942faa97",
            "a7b11817-205f-4e1a-98b5-e3c48b824bc3",
        ]
        embeddings_near_vectors = [
            [0.0 for _ in range(384)] for _ in range(len(film_uuids_for_near_embedding))
        ]
        for i, embd in enumerate(embeddings_near_vectors):
            embd[i] = 1.0
            for before_index in range(i):
                embd[before_index] = 0.9
        uuids_and_near_vectors = list(zip(film_uuids_for_near_embedding, embeddings_near_vectors))
        embeddings_far_vectors = [
            [round(random.random(), 3) * random.choice([-1, 1]) for _ in range(384)]
            for _ in range(len(film_uuids_for_far_embedding))
        ]
        uuids_and_far_vectors = list(zip(film_uuids_for_near_embedding, embeddings_far_vectors))
        return uuids_and_near_vectors + uuids_and_far_vectors

    async def prepare_films_data(self, es_write_data):
        uuids_with_vectors = self.prepare_uuids_and_vectors()

        es_data = [
            {
                "id": uuids_with_vectors[i][0],
                "title": "Film " + str(i) + (" some horror" if i % 2 == 0 else " some triller"),
                "imdb_rating": random.randrange(1, 10) + round(random.random(), 1),
                "description": f"D {i}",
                "type": "FREE",
                "embedding": uuids_with_vectors[i][-1],
            }
            for i in range(0, 20)
        ]
        es_data.sort(reverse=True, key=lambda film: film["imdb_rating"])
        await es_write_data(es_data, test_conf.elastic.index_films, Mapping.films)
        return es_data

    @pytest.mark.parametrize(
        "payload_data, expected_answer",
        [
            (
                {"vector": [0.0 if _ != 0 else 1.0 for _ in range(384)]},
                {
                    "correct_sequence_uuids": [
                        "3d825f60-9fff-4dfe-b294-1a45fa1e115d",
                        "0312ed51-8833-413f-bff5-0e139c11264a",
                        "025c58cd-1b7e-43be-9ffb-8571a613579b",
                        "cddf9b8f-27f9-4fe9-97cb-9e27d4fe3394",
                        "3b914679-1f5e-4cbd-8044-d13d35d5236c",
                        "516f91da-bd70-4351-ba6d-25e16b7713b7",
                        "c4c5e3de-c0c9-4091-b242-ceb331004dfd",
                        "4af6c9c9-0be0-4864-b1e9-7f87dd59ee1f",
                        "12a8279d-d851-4eb9-9d64-d690455277cc",
                        "118fd71b-93cd-4de5-95a4-e1485edad30e",
                    ],
                    "err_msg": "Неправльная последовательность найденных фильмов по вектору",
                },
            ),
            (
                {"vector": [1.0 for _ in range(384)]},
                {
                    "correct_sequence_uuids": [
                        "118fd71b-93cd-4de5-95a4-e1485edad30e",
                        "12a8279d-d851-4eb9-9d64-d690455277cc",
                        "4af6c9c9-0be0-4864-b1e9-7f87dd59ee1f",
                        "c4c5e3de-c0c9-4091-b242-ceb331004dfd",
                        "516f91da-bd70-4351-ba6d-25e16b7713b7",
                        "3b914679-1f5e-4cbd-8044-d13d35d5236c",
                        "cddf9b8f-27f9-4fe9-97cb-9e27d4fe3394",
                        "025c58cd-1b7e-43be-9ffb-8571a613579b",
                        "0312ed51-8833-413f-bff5-0e139c11264a",
                        "3d825f60-9fff-4dfe-b294-1a45fa1e115d",
                    ],
                    "err_msg": "Неправльная последовательность найденных фильмов по вектору",
                },
            ),
        ],
        ids=[
            "Test near vectors-1",
            "Test near vectors-2",
        ],
    )
    async def test_search_valid_vectos(
        self,
        es_write_data,
        make_post_request,
        payload_data: dict[str, list[float]],
        expected_answer: dict[str, list[str]],
    ):
        await self.prepare_films_data(es_write_data)
        body, status = await make_post_request(
            "/internal/search-by-vector",
            data=payload_data,
        )
        pp(body)
        assert status == HTTPStatus.OK
        uuids_from_response = [film.get("uuid", "invalid_uuid") for film in body]

        assert len(body) == len(
            expected_answer["correct_sequence_uuids"]
        ), f"Ожидалось 10 найденых фильмов, нашлось {len(body)}"

        assert uuids_from_response == expected_answer["correct_sequence_uuids"], expected_answer[
            "err_msg"
        ]

    # @pytest.mark.parametrize(
    #     "query_data, expected_answer",
    #     [
    #         (
    #             {"query": "horror", "page_size": 0},
    #             {"err_msg": "Ошибка валидации для page_size=0"},
    #         ),
    #         (
    #             {"query": "horror", "page_size": 101},
    #             {"err_msg": "Ошибка валидации для page_size=101"},
    #         ),
    #         (
    #             {"query": "horror", "page_number": 0},
    #             {"err_msg": "Ошибка валидации для page_number=0"},
    #         ),
    #     ],
    #     ids=[
    #         "Test page_size=0",
    #         "Test page_size=101",
    #         "Test page_number=0",
    #     ],
    # )
    # async def test_search_validation(
    #     self,
    #     make_get_request,
    #     query_data: dict[str, Any],
    #     expected_answer: dict[str, Any],
    #     create_user,
    # ):
    #     tokens_auth = await create_user(superuser_flag=True)
    #     headers = {"Authorization": f'Bearer {tokens_auth.get("access_token")}'}
    #     _, status = await make_get_request(
    #         "/films/search",
    #         params=query_data,
    #         headers=headers,
    #     )
    #     assert status == HTTPStatus.BAD_REQUEST, expected_answer["err_msg"]


#     @pytest.mark.parametrize(
#         "query_data, expected_answer",
#         [
#             (
#                 {"query": "horror", "page_size": 100},
#                 {
#                     "len_body": 50,
#                     "err_msg_len_body": "Ожидалось 50 фильмов с заголовком содержащим 'horror'",
#                     "err_msg_wrong_result": "Все заголовки должны содержать 'horror'",
#                 },
#             ),
#             (
#                 {"query": "triller", "page_size": 70},
#                 {
#                     "len_body": 51,
#                     "err_msg_len_body": "Ожидалось 51 фильмов с заголовком содержащим 'triller'",
#                     "err_msg_wrong_result": "Все заголовки должны содержать 'horror'",
#                 },
#             ),
#             (
#                 {"query": "unknown", "page_size": 10},
#                 {
#                     "len_body": 0,
#                     "err_msg_len_body": "Ожидался пустой результат для 'unknown'",
#                     "err_msg_wrong_result": "Все заголовки должны содержать 'horror'",
#                 },
#             ),
#         ],
#         ids=[
#             "Test query='horror'",
#             "Test query='triller'",
#             "Test query='unknown'",
#         ],
#     )
#     async def test_search_by_phrase(
#         self,
#         es_write_data,
#         make_get_request,
#         query_data: dict[str, Any],
#         expected_answer: dict[str, Any],
#         create_user,
#     ):
#         tokens_auth = await create_user(superuser_flag=True)
#         headers = {"Authorization": f'Bearer {tokens_auth.get("access_token")}'}

#         await self.prepare_films_data(es_write_data, count=101)

#         body, status = await make_get_request(
#             "/films/search",
#             params=query_data,
#             headers=headers,
#         )
#         titles = {item["title"] for item in body}

#         assert status == HTTPStatus.OK
#         assert len(body) == expected_answer["len_body"], expected_answer["err_msg_len_body"]
#         assert all(
#             True if "unknown" in title else query_data["query"] in title for title in titles
#         ), expected_answer["err_msg_wrong_result"]


# @pytest.mark.asyncio
# class TestFilmsList:
#     """Тесты для эндпоинта /api/v1/films"""

#     def _get_genre_ids(self):
#         return [uuid4() for _ in range(3)]

#     async def prepare_films_data(
#         self,
#         es_write_data,
#         count=10,
#     ):
#         genre_item_one_genre = [
#             {
#                 "id": "526769d7-df18-4661-9aa6-49ed24e9dfd8",
#                 "name": "horror",
#             },
#         ]
#         genre_item_many_genre = [
#             {"id": "6a0a479b-cfec-41ac-b520-41b2b007b611", "name": "triller"},
#             {"id": "7f6a9006-dba4-4b63-ac34-b56c3e8a7e8f", "name": "detective"},
#         ]
#         es_data = [
#             {
#                 "id": str(uuid4()),
#                 "title": "Film "
#                 + str(i)
#                 + (" some horror" if i % 2 == 0 else " some triller and detective"),
#                 "imdb_rating": random.randrange(1, 9) + round(random.random(), 1),
#                 "description": "Description ",
#                 "genres": genre_item_one_genre if i % 2 == 0 else genre_item_many_genre,
#                 "type": "FREE",
#             }
#             for i in range(count)
#         ]
#         es_data.sort(key=lambda film: film["imdb_rating"])
#         es_data[0]["imdb_rating"] = 0.1
#         es_data[-1]["imdb_rating"] = 9.9

#         await es_write_data(es_data, test_conf.elastic.index_films, Mapping.films)
#         return es_data

#     @pytest.mark.parametrize(
#         "query_data, expected_answer",
#         [
#             (
#                 {"sort": "-imdb_rating", "page_size": 0},
#                 {"err_msg": "Ошибка валидации для page_size=0"},
#             ),
#             (
#                 {"sort": "-imdb_rating", "page_size": 101},
#                 {"err_msg": "Ошибка валидации для page_size=101"},
#             ),
#             (
#                 {"sort": "not-valid-sort", "page_size": 50},
#                 {"err_msg": "Ошибка валидации для sort=not-valid-sort"},
#             ),
#             (
#                 {"genre": "not-valid-uuid", "page_size": 50},
#                 {"err_msg": "Ошибка валидации для genre=not-valid-uuid"},
#             ),
#         ],
#         ids=[
#             "Test page_size=0",
#             "Test page_size=101",
#             "Test sort=not-valid-sort",
#             "Test genre=not-valid-uuid",
#         ],
#     )
#     async def test_films_validation(
#         self,
#         make_get_request,
#         query_data: dict[str, Any],
#         expected_answer: dict[str, Any],
#         create_user,
#     ):
#         tokens_auth = await create_user(superuser_flag=True)
#         headers = {"Authorization": f'Bearer {tokens_auth.get("access_token")}'}
#         _, status = await make_get_request("/films", params=query_data, headers=headers)
#         assert status == HTTPStatus.BAD_REQUEST, expected_answer["err_msg"]

#     @pytest.mark.parametrize(
#         "query_data, expected_answer",
#         [
#             (
#                 {"sort": "-imdb_rating", "page_size": 10},
#                 {
#                     "index": 0,
#                     "imdb_rating": 9.9,
#                     "err_msg_status_code": "Ожидался статус код 200",
#                     "err_msg_len_body": "Ожидалось 10 фильмов",
#                     "err_msg_wrong_result": "Ожидался рейтинг 0.1",
#                 },
#             ),
#             (
#                 {"sort": "imdb_rating", "page_size": 10},
#                 {
#                     "index": 0,
#                     "imdb_rating": 0.1,
#                     "err_msg_status_code": "Ожидался статус код 200",
#                     "err_msg_len_body": "Ожидалось 10 фильмов",
#                     "err_msg_wrong_result": "Ожидался рейтинг 9.9",
#                 },
#             ),
#         ],
#         ids=[
#             "Test sort='-imdb_rating'",
#             "Test sort='imdb_rating'",
#         ],
#     )
#     async def test_films_sort(
#         self,
#         es_write_data,
#         make_get_request,
#         query_data: dict[str, Any],
#         expected_answer: dict[str, Any],
#         create_user,
#     ):
#         """Проверка вывода всех фильмов"""
#         await self.prepare_films_data(es_write_data, count=10)
#         tokens_auth = await create_user(superuser_flag=True)
#         headers = {"Authorization": f'Bearer {tokens_auth.get("access_token")}'}

#         body, status = await make_get_request(
#             "/films",
#             params=query_data,
#             headers=headers,
#         )

#         assert status == HTTPStatus.OK
#         assert len(body) == 10, expected_answer["err_msg_len_body"]
#         assert body[0]["imdb_rating"] == expected_answer["imdb_rating"]

#     @pytest.mark.parametrize(
#         "query_data, expected_answer",
#         [
#             (
#                 {"genre": "526769d7-df18-4661-9aa6-49ed24e9dfd8", "page_size": 10},
#                 {
#                     "genre": "horror",
#                     "err_msg_status_code": "Ожидался статус код 200",
#                     "err_msg_len_body": "Ожидалось 10 фильмов",
#                     "err_msg_wrong_result": "Ожидался рейтинг 0.1",
#                 },
#             ),
#             (
#                 [
#                     ("genre", "6a0a479b-cfec-41ac-b520-41b2b007b611"),
#                     ("genre", "7f6a9006-dba4-4b63-ac34-b56c3e8a7e8f"),
#                     ("page_size", "10"),
#                 ],
#                 {
#                     "genre": "triller",
#                     "second_genre": "detective",
#                     "err_msg_status_code": "Ожидался статус код 200",
#                     "err_msg_len_body": "Ожидалось 10 фильмов",
#                     "err_msg_wrong_result": "Ожидался рейтинг 9.9",
#                 },
#             ),
#         ],
#         ids=[
#             "Test genre with one GET parametr",
#             "Test genre with two GET parametr",
#         ],
#     )
#     async def test_films_genre(
#         self,
#         es_write_data,
#         make_get_request,
#         query_data: dict[str, Any],
#         expected_answer: dict[str, Any],
#         create_user,
#     ):
#         await self.prepare_films_data(es_write_data, count=10)
#         tokens_auth = await create_user(superuser_flag=True)
#         headers = {"Authorization": f'Bearer {tokens_auth.get("access_token")}'}

#         body, status = await make_get_request(
#             "/films",
#             params=query_data,
#             headers=headers,
#         )

#         assert status == HTTPStatus.OK
#         assert len(body) == 5
#         assert all(expected_answer["genre"] in item["title"] for item in body)
#         if expected_answer.get("second_genre"):
#             assert all(expected_answer["second_genre"] in item["title"] for item in body)

#     @pytest.mark.parametrize(
#         "query_data, expected_answer",
#         [
#             (
#                 {"genre": "526769d7-df18-4661-9aa6-49ed24e9dds3", "page_size": 10},
#                 {
#                     "cached_data": False,
#                     "cach_key": (
#                         "films:-imdb_rating:page1:size10:"
#                         "genres526769d7-df18-4661-9aa6-49ed24e9dds3:ARCHIVED-FREE-PAID"
#                     ),
#                 },
#             ),
#             (
#                 {"genre": "526769d7-df18-4661-9aa6-49ed24e9dfd8", "page_size": 10},
#                 {
#                     "cached_data": True,
#                     "cach_key": (
#                         "films:-imdb_rating:page1:size10:"
#                         "genres526769d7-df18-4661-9aa6-49ed24e9dfd8:ARCHIVED-FREE-PAID"
#                     ),
#                 },
#             ),
#             (
#                 [
#                     ("genre", "6a0a479b-cfec-41ac-b520-41b2b007b611"),
#                     ("genre", "7f6a9006-dba4-4b63-ac34-b56c3e8a7e8f"),
#                     ("page_size", 10),
#                 ],
#                 {
#                     "cached_data": True,
#                     "cach_key": (
#                         "films:-imdb_rating:page1:size10:"
#                         "genres6a0a479b-cfec-41ac-b520-41b2b007b611-"
#                         "7f6a9006-dba4-4b63-ac34-b56c3e8a7e8f:ARCHIVED-FREE-PAID"
#                     ),
#                 },
#             ),
#         ],
#         ids=[
#             "Test cache without request",
#             "Test cache with one GET parametr",
#             "Test cache with two GET parametrs",
#         ],
#     )
#     async def test_films_with_cache(
#         self,
#         es_write_data,
#         make_get_request,
#         redis_test,
#         query_data: dict[str, Any],
#         expected_answer: dict[str, Any],
#         create_user,
#     ):
#         await self.prepare_films_data(es_write_data, count=10)
#         tokens_auth = await create_user(superuser_flag=True)
#         headers = {"Authorization": f'Bearer {tokens_auth.get("access_token")}'}
#         body, status = await make_get_request(
#             "/films",
#             params=query_data,
#             headers=headers,
#         )

#         cache = await redis_test(
#             key=expected_answer["cach_key"],
#             cached_data=expected_answer.get("cached_data"),
#         )

#         if expected_answer.get("cached_data"):
#             cache_titles = {item["title"] for item in cache}
#             api_titles = {item["title"] for item in body}
#             assert cache_titles == api_titles, "Кэш должен совпадать с ответом API"


# @pytest.mark.asyncio
# class TestFilmsDetail:
#     @pytest.mark.parametrize(
#         "url_path, expected_answer",
#         [
#             (
#                 {
#                     "UUID": "1d825f60-9fff-4dfe-b294-1a45fa1e115d",
#                 },
#                 {
#                     "body": {
#                         "actors": [],
#                         "description": "asdasdasdsa",
#                         "directors": [],
#                         "genre": [],
#                         "imdb_rating": 10.0,
#                         "title": "Brother 1",
#                         "uuid": "1d825f60-9fff-4dfe-b294-1a45fa1e115d",
#                         "writers": [],
#                         "type": "FREE",
#                     },
#                     "cach_key": "1d825f60-9fff-4dfe-b294-1a45fa1e115d",
#                     "invalid_uuid": False,
#                     "no_existing_uuid": False,
#                     "err_msg_status_code": "Ожидался статус код 200",
#                     "err_msg_wrong_result": "Тело ответа не совпадает с ожидаемым",
#                 },
#             ),
#             (
#                 {
#                     "UUID": "invalid UUID",
#                 },
#                 {
#                     "body": {},
#                     "cach_key": "",
#                     "invalid_uuid": True,
#                     "no_existing_uuid": False,
#                     "err_msg_status_code": "Ожидался статус код 400",
#                 },
#             ),
#             (
#                 {
#                     "UUID": "8d825f60-9fff-4dfe-b294-1a45fa1e115d",
#                 },
#                 {
#                     "body": None,
#                     "cach_key": "",
#                     "invalid_uuid": False,
#                     "no_existing_uuid": True,
#                     "err_msg_status_code": "Ожидался статус код 200",
#                     "err_msg_wrong_result": "Тело ответа ожидалось null",
#                 },
#             ),
#         ],
#         ids=[
#             "Test detail",
#             "Test invalid uuid",
#             "Test no existing uuid",
#         ],
#     )
#     async def test_film_by_uuid(
#         self,
#         es_write_data,
#         make_get_request,
#         redis_test,
#         url_path: dict[str, Any],
#         expected_answer: dict[str, Any],
#         create_user,
#     ):
#         es_data = [
#             {
#                 "id": "1d825f60-9fff-4dfe-b294-1a45fa1e115d",
#                 "title": "Brother 1",
#                 "imdb_rating": 10,
#                 "description": "asdasdasdsa",
#                 "type": "FREE",
#             },
#             {
#                 "id": "2d825f60-9fff-4dfe-b294-1a45fa1e115d",
#                 "title": "Brother 2",
#                 "imdb_rating": 10,
#                 "description": "asdasdasdsa",
#                 "type": "FREE",
#             },
#         ]
#         await es_write_data(es_data, test_conf.elastic.index_films, Mapping.films)
#         tokens_auth = await create_user(superuser_flag=True)
#         headers = {"Authorization": f'Bearer {tokens_auth.get("access_token")}'}
#         body, status = await make_get_request(
#             f"/films/{url_path['UUID']}",
#             headers=headers,
#         )

#         if expected_answer.get("invalid_uuid"):
#             assert status == HTTPStatus.BAD_REQUEST, expected_answer.get(
#                 "err_msg_status_code",
#             )
#             return

#         if expected_answer.get("no_existing_uuid"):
#             assert status == HTTPStatus.OK, expected_answer.get("err_msg_status_code")
#             assert body == expected_answer["body"], expected_answer.get(
#                 "err_msg_wrong_result",
#             )
#             return

#         assert status == HTTPStatus.OK, expected_answer.get("err_msg_status_code")
#         assert body == expected_answer["body"], expected_answer.get(
#             "err_msg_wrong_result",
#         )

#         cache = await redis_test(key=expected_answer["cach_key"])
#         assert cache is not None
#         assert cache == expected_answer["body"], expected_answer.get(
#             "err_msg_wrong_result",
#         )
