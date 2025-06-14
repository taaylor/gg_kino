import pytest
from clickhouse_driver import Client

from tests.functional.core.settings import test_conf


@pytest.fixture(name="clickhouse_client", scope="session")
def clickhouse_client():
    client = Client(
        test_conf.clickhouse.host,
        test_conf.clickhouse.port,
        user=test_conf.clickhouse.user,
        password=test_conf.clickhouse.default_password,
    )

    yield client

    client.disconnect()
