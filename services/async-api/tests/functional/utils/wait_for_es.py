from elasticsearch import ConnectionError, Elasticsearch, TransportError
from tests.functional.core.config_log import get_logger
from tests.functional.core.settings import test_conf
from tests.functional.utils.decorators import backoff

logger = get_logger("wait_for_es")


@backoff(exception=(ConnectionError, TransportError))
def check_elasticsearch():
    es_client = Elasticsearch(hosts=test_conf.elastic.es_host)
    try:
        if not es_client.ping():
            raise ConnectionError("Elastic ping failed")
        logger.debug("Elastic готов к тестированию")
        return True
    finally:
        # после каждой неудачной попытки закрываем соединение
        # чтобы не было утечек ресурсов
        es_client.close()


if __name__ == "__main__":
    check_elasticsearch()
