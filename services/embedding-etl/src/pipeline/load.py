# from clickhouse_driver import Client
# from clickhouse_driver.dbapi import DatabaseError
# from core.logger_config import get_logger
# from utils.decorators import backoff

# logger = get_logger(__name__)


# @backoff(exception=(DatabaseError,))
# def load_to_clickhouse(
#     data: list[tuple],
#     client: Client,
#     database: str,
#     table_name_dist: str,
# ):
#     """Загружает данные в ClickHouse.

#     :param data: Список кортежей с данными.
#     :param database: Имя базы данных.
#     :param table_name_dist: Имя таблицы в ClickHouse.
#     """
#     client.execute(
#         f"""
#         INSERT INTO {database}.{table_name_dist}
#         (
#             user_session,
#             user_uuid,
#             user_agent,
#             ip_address,
#             film_uuid,
#             event_params,
#             event_type,
#             message_event,
#             event_timestamp,
#             user_timestamp
#         )
#         VALUES
#         """,
#         data,
#     )
#     logger.info(f"Загружено {len(data)} записей в таблицу {database}.{table_name_dist}")
