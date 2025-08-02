import asyncio
from http import HTTPMethod
from typing import Any

import jwt
import pytest
from tests.functional.core.logger_conf import get_logger
from tests.functional.core.settings import test_conf
from tests.functional.testdata.model_enum import RecsSourceType
from tests.functional.testdata.model_orm import UserRecs

logger = get_logger(__name__)


@pytest.mark.asyncio
class TestRecsProfile:

    async def _fetch_user_and_token(
        self,
        create_user,
    ) -> tuple[str, str]:
        """Функция возвращает id пользователя и его access токен"""
        # Получает пользователя для теста
        access_token = (await create_user())["access_token"]
        user_id = jwt.decode(
            access_token, options={"verify_signature": False}, algorithms=["RS256"]
        )["user_id"]
        logger.info(f"Получен user_id пользователя: {user_id}")

        return user_id, f"Bearer {access_token}"

    async def _fetch_recs(self, make_request, user_id) -> tuple[int, int]:
        recs_count = 0
        recs_dims = 0

        recs_url = test_conf.recs_api.get_url
        recs_data = {"user_ids": [f"{user_id}"]}
        recs_status, recs_body = await make_request(
            method=HTTPMethod.POST, url=recs_url, data=recs_data
        )
        logger.info(f"От сервиса профиля рекомендаций получен ответ status: {recs_status}")

        recs_emb = recs_body.get("recs")[0].get("embeddings")
        if recs_emb:
            recs_count = len(recs_emb)
            recs_dims = len(recs_emb[0].get("embedding"))

        logger.info(f"Количество эмбедингов в ответе: {recs_count}, размерность: {recs_dims}")

        return recs_count, recs_dims

    @pytest.mark.parametrize(
        "content_api_params, expected_answer",
        [
            (
                {"url": test_conf.contentapi.get_rating_url, "body": {"score": 1}},
                {
                    "recs_in_db": False,
                    "result_recs_count": 0,
                    "result_recs_dims": 0,
                    "rec_source_type": None,
                },
            ),
            (
                {"url": test_conf.contentapi.get_rating_url, "body": {"score": 10}},
                {
                    "recs_in_db": True,
                    "result_recs_count": 1,
                    "result_recs_dims": 384,
                    "rec_source_type": RecsSourceType.HIGH_RATING,
                },
            ),
            (
                {
                    "url": test_conf.contentapi.get_bookmark_url,
                    "body": {"comment": "Звучит хайпово, посмотрю на НГ"},
                },
                {
                    "recs_in_db": True,
                    "result_recs_count": 1,
                    "result_recs_dims": 384,
                    "rec_source_type": RecsSourceType.ADD_BOOKMARKS,
                },
            ),
        ],
        ids=[
            "Check with sufficient score for recommendation recording",
            "Check with bookmark add recommendation recording",
        ],
    )
    async def test_set_recs_profile(
        self,
        make_request,
        create_user,
        fetch_user_recs,
        content_api_params: dict[str, Any],
        expected_answer: dict[str, Any],
    ) -> None:

        # Получаю юзера для теста
        user_id, token = await self._fetch_user_and_token(create_user)

        # Проверяю, что рекомендаций для пользователя нет
        recs_count, recs_dims = await self._fetch_recs(make_request, user_id)
        assert recs_count == 0
        assert recs_dims == 0

        # Создаю оценку фильма или закладку от пользователя
        content_url = content_api_params["url"]
        content_data = content_api_params["body"]
        headers = {"Authorization": f"{token}"}
        await make_request(
            method=HTTPMethod.POST, url=content_url, data=content_data, headers=headers
        )

        # Жду пока обработается сообщение в Kafka
        await asyncio.sleep(2)

        # Проверяю запись оценки в БД
        user_recs: UserRecs = await fetch_user_recs(user_id)
        if expected_answer["recs_in_db"]:
            assert user_recs.rec_source_type == expected_answer["rec_source_type"]
        else:
            assert user_recs is None

        # Проверяю наличие рекомендации в ответе API
        recs_count, recs_dims = await self._fetch_recs(make_request, user_id)

        assert recs_count == expected_answer["result_recs_count"]
        assert recs_dims == expected_answer["result_recs_dims"]
