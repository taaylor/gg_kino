import psycopg
from psycopg import DatabaseError, OperationalError
from tests.functional.core.config_log import get_logger
from tests.functional.core.settings import test_conf
from tests.functional.utils.decorators import backoff

logger = get_logger("wait_for_postgres")


@backoff(exception=(OperationalError, DatabaseError))
def check_postgres():
    try:
        with psycopg.connect(
            host=test_conf.postgres.host,
            port=test_conf.postgres.port,
            user=test_conf.postgres.user,
            password=test_conf.postgres.password,
            dbname=test_conf.postgres.db,
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                if not result or result[0] != 1:
                    raise OperationalError("PostgreSQL ping query failed")
        logger.debug("PostgreSQL готов к тестированию")
        return True
    except (OperationalError, DatabaseError) as e:
        logger.error(f"Ошибка подключения к PostgreSQL: {e}")
        raise


if __name__ == "__main__":
    check_postgres()
