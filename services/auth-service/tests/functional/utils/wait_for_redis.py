from redis import Redis
from redis.exceptions import ConnectionError, RedisError, TimeoutError
from tests.functional.core.config_log import get_logger
from tests.functional.core.settings import test_conf
from tests.functional.utils.decorators import backoff

logger = get_logger("wait_for_redis")


@backoff(exception=(ConnectionError, TimeoutError, RedisError))
def check_redis():
    redis_client = Redis(
        host=test_conf.redis.host,
        port=test_conf.redis.port,
        username=test_conf.redis.user,
        password=test_conf.redis.password,
        db=test_conf.redis.db,
    )
    try:
        if not redis_client.ping():
            raise ConnectionError("Redis ping failed")
        logger.debug("Redis готов к тестированию")
        return True
    finally:
        redis_client.close()


if __name__ == "__main__":
    check_redis()
