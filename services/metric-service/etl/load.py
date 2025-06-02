import logging

from clickhouse_driver import Client

logger = logging.getLogger(__name__)


def load_to_clickhouse(data: list[tuple], host: str, port: str, db_name: str, table_name_dist: str):
    """
    Загружает данные в ClickHouse.

    :param data: Список кортежей с данными.
    :param db_name: Имя базы данных.
    :param table_name_dist: Имя таблицы в ClickHouse.
    """
    try:
        client = Client(host=host, port=port, database=db_name)
        client.execute(
            # kinoservice.metrics_distributed
            """
            INSERT INTO {db_name}.{table_name_dist}
            (
                id,
                user_session,
                user_uuid,
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
                db_name=db_name,
                table_name_dist=table_name_dist,
            ),
            data,
        )
        logger.info(f"Загружено {len(data)} записей в таблицу {db_name}.{table_name_dist}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке в ClickHouse: {e}")
    finally:
        client.disconnect()
