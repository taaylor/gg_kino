import random
import time
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Generator

import pytest
import requests
from clickhouse_driver import Client as ClickClient
from faker import Faker
from tests.functional.core.settings import test_conf
from tests.functional.testdata.model import EventRequest


class TestMetrics:

    def get_data_request(self, value_item: int) -> Generator[EventRequest, None, None]:
        faker = Faker()

        for _ in range(value_item):
            yield EventRequest(
                film_uuid=uuid.uuid4(),
                event_type=random.choice(["like", "comment", "watch_progress"]),
                message_event=faker.text(max_nb_chars=200),
                user_timestamp=datetime.now(timezone.utc),
                event_params={"value": faker.image_url(), "params": faker.phone_number()},
            )

    def test_metrics_request(self, clickhouse_client: ClickClient):

        value_item = 500
        url = test_conf.metricsapi.get_url_api() + "/metric"
        status_codes = [None] * value_item
        gen = self.get_data_request(value_item)

        for idx, data in enumerate(gen, start=0):
            response = requests.post(
                url=url, data=data.model_dump_json(), headers={"Content-Type": "application/json"}
            )

            if response.status_code == HTTPStatus.NO_CONTENT:
                status_codes[idx] = True
            else:
                status_codes[idx] = False

        time.sleep(20)  # ждем пока etl переложит данные в clickhouse

        result = clickhouse_client.execute(
            f"""
            SELECT COUNT(*)
            FROM {test_conf.clickhouse.database}.{test_conf.clickhouse.table_name_dist}
            """
        )

        assert result[0][0] == value_item
        assert sum(status_codes) == value_item

    @pytest.mark.skip(reason="Пока не работает ratelimiter, нужно затащить nginx =)")
    def test_ratelimiter(self):
        """Лимитер ограничивает 1000 RPM по конкретному ip-адресу"""

        value_item = 2000
        url = test_conf.metricsapi.get_url_api() + "/metric"
        status_codes = set()
        gen = self.get_data_request(value_item)

        for data in gen:
            response = requests.post(
                url=url, data=data.model_dump_json(), headers={"Content-Type": "application/json"}
            )

            status_codes.add(response.status_code)

        assert HTTPStatus.TOO_MANY_REQUESTS in status_codes
