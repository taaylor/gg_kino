import asyncio
from http import HTTPMethod, HTTPStatus
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

    @pytest.mark.parametrize(
        "score, expected_answer",
        [
            (10, {"status": HTTPStatus.CREATED, "recs_in_db": True}),
            (1, {"status": HTTPStatus.CREATED, "recs_in_db": False}),
        ],
        ids=[
            "Check with sufficient score for recommendation recording",
            "Check with INsufficient score for recommendation recording",
        ],
    )
    async def test_set_recs_profile_from_score(
        self,
        make_request,
        create_user,
        fetch_user_recs,
        score: int,
        expected_answer: dict[str, Any],
    ) -> None:
        # Получает пользователя для теста
        access_token = (await create_user())["access_token"]
        user_id = jwt.decode(
            access_token, options={"verify_signature": False}, algorithms=["RS256"]
        )["user_id"]

        recs_url = test_conf.recs_api.get_url
        recs_data = {"user_ids": [f"{user_id}"]}

        recs_status, recs_body = await make_request(
            method=HTTPMethod.POST, url=recs_url, data=recs_data
        )
        logger.info(f"Получен user_id пользователя: {user_id}")

        content_url = test_conf.contentapi.get_rating_url
        content_data = {"score": score}
        headers = {"Authorization": f"Bearer {access_token}"}
        content_status, content_body = await make_request(
            method=HTTPMethod.POST, url=content_url, data=content_data, headers=headers
        )

        await asyncio.sleep(5)

        user_recs: UserRecs = await fetch_user_recs(user_id)

        assert recs_status == HTTPStatus.OK
        assert access_token is not None
        assert content_status == expected_answer["status"]

        if expected_answer["recs_in_db"]:
            assert user_recs.rec_source_type == RecsSourceType.HIGH_RATING
        else:
            assert user_recs is None
