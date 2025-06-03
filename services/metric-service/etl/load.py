import logging

from clickhouse_driver import Client

logger = logging.getLogger(__name__)


def load_to_clickhouse(
    data: list[tuple],
    host: str,
    port: str,
    user: str,
    password: str,
    database: str,
    table_name_dist: str,
):
    """
    Загружает данные в ClickHouse.

    :param data: Список кортежей с данными.
    :param database: Имя базы данных.
    :param table_name_dist: Имя таблицы в ClickHouse.
    """
    try:
        client = Client(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
        )
        client.execute(
            # kinoservice.metrics_distributed
            """
            INSERT INTO {database}.{table_name_dist}
            (
                id,
                user_session,
                user_uuid,
                user_agent,
                ip_address,
                film_uuid,
                event_params,
                event_type,
                message_event,
                event_timestamp,
                user_timestamp
            )
            VALUES
            """.format(
                database=database,
                table_name_dist=table_name_dist,
            ),
            data,
        )
        logger.info(f"Загружено {len(data)} записей в таблицу {database}.{table_name_dist}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке в ClickHouse: {e}")
    finally:
        client.disconnect()
