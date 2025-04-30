import psycopg
from psycopg import DatabaseError, OperationalError
from pytest import fixture
from tests.functional.core.config_log import get_logger
from tests.functional.core.settings import test_conf

logger = get_logger(__name__)


@fixture(name="postgres_client", scope="session")
def postgres_client():
    """
    Фикстура для создания синхронного клиента PostgreSQL.
    """
    try:
        conn = psycopg.connect(
            host=test_conf.postgres.host,
            port=test_conf.postgres.port,
            user=test_conf.postgres.user,
            password=test_conf.postgres.password,
            dbname=test_conf.postgres.db,
        )
        logger.debug("PostgreSQL клиент успешно подключён")
        yield conn
    except (OperationalError, DatabaseError) as e:
        logger.error(f"Ошибка подключения к PostgreSQL: {e}")
        raise
    finally:
        conn.close()
        logger.debug("PostgreSQL клиент закрыт")


@fixture(name="postgres_test")
def postgres_test(postgres_client: psycopg.Connection):
    """
    Фикстура для выполнения SQL-запросов к PostgreSQL.
    """

    def inner(query: str, params: tuple | dict | None = None) -> list:
        """
        Выполняет SQL-запрос и возвращает результаты.

        :param query: SQL-запрос (например, 'SELECT * FROM users WHERE id = %s')
        :param params: Параметры для запроса (кортеж или словарь)
        :return: Список строк результата
        """
        try:
            with postgres_client.cursor() as cur:
                cur.execute(query, params)
                # Проверяем, есть ли результат (SELECT возвращает строки, другие запросы — нет)
                if cur.description:  # Если есть столбцы в результате
                    result = cur.fetchall()
                    logger.debug(f"PostgreSQL запрос выполнен: {query}, результат: {result}")
                    return result
                logger.debug(f"PostgreSQL запрос выполнен: {query}, без результата")
                return []
        except (OperationalError, DatabaseError) as e:
            logger.error(f"Ошибка выполнения запроса PostgreSQL: {e}")
            raise

    return inner
