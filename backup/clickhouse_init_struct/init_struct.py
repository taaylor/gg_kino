import os

import dotenv
from clickhouse_driver import Client, errors

dotenv.load_dotenv(dotenv_path=dotenv.find_dotenv())

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST")
PASSWORD = os.getenv("CLICKHOUSE_PASSWORD")
USER = os.getenv("CLICKHOUSE_USER")
TABLE_NAME = "metrics"
TABLE_NAME_DIST = "metrics_dst"
DB_NAME = "kinoservice"
CLUSTER_NAME = "kinoservice_cluster"
MV_TRENDS = "film_trends_mv"
MV_TRENDS_AGGR = "trends_arggr_mv"
TABLE_TRENDS_AGGR_DATA = "trends_arggr_data"
TABLE_TRENDS_RAW = "trends_raw_data"
TABLE_TRENDS_AGGR_DATA_DIST = "trends_arggr_data_dist"
TABLE_TRENDS_RAW_DIST = "trends_raw_data_dist"


def create_schema_trends(client: Client) -> None:
    client.execute(
        """
        CREATE TABLE IF NOT EXISTS {DB_NAME}.{TABLE_TRENDS_RAW}
        ON CLUSTER {CLUSTER_NAME}
        (
            event_date Date,
            film_uuid UUID,
            event_type String,
            like_score Float64,
            watch_score Float64
        )
        ENGINE = ReplicatedMergeTree(
            '/clickhouse/tables/{cluster}/{shard}/{TABLE_TRENDS_RAW}',
            '{replica}'
        )
        PARTITION BY toYYYYMM(event_date)
        ORDER BY (event_date, film_uuid)
    """.format(
            DB_NAME=DB_NAME,
            TABLE_TRENDS_RAW=TABLE_TRENDS_RAW,
            CLUSTER_NAME=CLUSTER_NAME,
            cluster="{cluster}",
            shard="{shard}",
            replica="{replica}",
        )
    )

    client.execute(
        """
        CREATE TABLE IF NOT EXISTS {DB_NAME}.{TABLE_TRENDS_RAW_DIST}
        ON CLUSTER {CLUSTER_NAME}
        (
            event_date Date,
            film_uuid UUID,
            event_type String,
            like_score Float64,
            watch_score Float64
        )
        ENGINE = Distributed(
            '{CLUSTER_NAME}',
            '{DB_NAME}',
            '{TABLE_TRENDS_RAW}',
            rand()
        )
    """.format(
            DB_NAME=DB_NAME,
            TABLE_TRENDS_RAW_DIST=TABLE_TRENDS_RAW_DIST,
            CLUSTER_NAME=CLUSTER_NAME,
            TABLE_TRENDS_RAW=TABLE_TRENDS_RAW,
        )
    )

    client.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS {DB_NAME}.{MV_TRENDS}
        ON CLUSTER {CLUSTER_NAME}
        TO {DB_NAME}.{TABLE_TRENDS_RAW_DIST}
        AS
        SELECT
            toDate(event_timestamp) AS event_date,
            film_uuid,
            event_type,
            IF(event_type = 'like' AND mapContains(event_params, 'rating'),
            IF(toInt32OrZero(event_params['rating']) > 5, 1, -1),
            0
            ) AS like_score,
            IF (event_type = 'watch_progress', 0.1, 0) AS watch_score
        FROM {DB_NAME}.{TABLE_NAME_DIST}
        WHERE event_type IN ('like', 'watch_progress') AND film_uuid IS NOT NULL
    """.format(
            DB_NAME=DB_NAME,
            MV_TRENDS=MV_TRENDS,
            TABLE_TRENDS_RAW_DIST=TABLE_TRENDS_RAW_DIST,
            TABLE_NAME_DIST=TABLE_NAME_DIST,
            CLUSTER_NAME=CLUSTER_NAME,
        )
    )

    client.execute(
        """
        CREATE TABLE IF NOT EXISTS {DB_NAME}.{TABLE_TRENDS_AGGR_DATA}
        ON CLUSTER {CLUSTER_NAME}
        (
            film_uuid UUID,
            total_score AggregateFunction(sum, Float64),
            event_date Date,
        )
        ENGINE = ReplicatedAggregatingMergeTree(
            '/clickhouse/tables/{cluster}/{shard}/{TABLE_TRENDS_AGGR_DATA}',
            '{replica}'
        )
        PARTITION BY toYYYYMM(event_date)
        ORDER BY (event_date, film_uuid);
    """.format(
            DB_NAME=DB_NAME,
            TABLE_TRENDS_AGGR_DATA=TABLE_TRENDS_AGGR_DATA,
            CLUSTER_NAME=CLUSTER_NAME,
            cluster="{cluster}",
            shard="{shard}",
            replica="{replica}",
        )
    )

    client.execute(
        """
        CREATE TABLE IF NOT EXISTS {DB_NAME}.{TABLE_TRENDS_AGGR_DATA_DIST}
        ON CLUSTER {CLUSTER_NAME}
        (
            film_uuid UUID,
            total_score AggregateFunction(sum, Float64),
            event_date Date,
        )
        ENGINE = Distributed(
            '{CLUSTER_NAME}',
            '{DB_NAME}',
            '{TABLE_TRENDS_AGGR_DATA}',
            rand()
        )
    """.format(
            DB_NAME=DB_NAME,
            TABLE_TRENDS_AGGR_DATA_DIST=TABLE_TRENDS_AGGR_DATA_DIST,
            CLUSTER_NAME=CLUSTER_NAME,
            TABLE_TRENDS_AGGR_DATA=TABLE_TRENDS_AGGR_DATA,
        )
    )

    client.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS {DB_NAME}.{MV_TRENDS_AGGR}
        ON CLUSTER {CLUSTER_NAME}
        TO {DB_NAME}.{TABLE_TRENDS_AGGR_DATA_DIST}
        AS
        SELECT
            film_uuid,
            event_date,
            sumState(like_score + watch_score) AS total_score
        FROM {DB_NAME}.{TABLE_TRENDS_RAW_DIST}
        GROUP BY (event_date, film_uuid);
    """.format(
            DB_NAME=DB_NAME,
            MV_TRENDS_AGGR=MV_TRENDS_AGGR,
            TABLE_TRENDS_AGGR_DATA_DIST=TABLE_TRENDS_AGGR_DATA_DIST,
            TABLE_TRENDS_RAW_DIST=TABLE_TRENDS_RAW_DIST,
            CLUSTER_NAME=CLUSTER_NAME,
        )
    )


def create_schema_metrics(client: Client) -> None:

    client.execute(
        """
        CREATE DATABASE IF NOT EXISTS {DB_NAME}
        ON CLUSTER {CLUSTER_NAME}
    """.format(
            DB_NAME=DB_NAME, CLUSTER_NAME=CLUSTER_NAME
        ),
    )

    client.execute(
        """
        CREATE TABLE IF NOT EXISTS {DB_NAME}.{TABLE_NAME}
        ON CLUSTER {CLUSTER_NAME}
        (
            id UUID DEFAULT generateUUIDv4(),
            user_session Nullable(UUID),
            user_uuid Nullable(UUID),
            user_agent String,
            ip_address Nullable(String),
            film_uuid Nullable(UUID),
            event_params Map(String, String),
            event_type String,
            message_event String,
            event_timestamp DateTime,
            user_timestamp DateTime
        )
        ENGINE = ReplicatedMergeTree(
            '/clickhouse/tables/{cluster}/{shard}/{TABLE_NAME}',
            '{replica}'
        )
        PARTITION BY toYYYYMMDD(event_timestamp)
        ORDER BY event_timestamp
        TTL event_timestamp + INTERVAL 360 DAY
        SETTINGS index_granularity = 8192
    """.format(
            DB_NAME=DB_NAME,
            TABLE_NAME=TABLE_NAME,
            CLUSTER_NAME=CLUSTER_NAME,
            cluster="{cluster}",
            shard="{shard}",
            replica="{replica}",
        ),
    )

    client.execute(
        """
        CREATE TABLE IF NOT EXISTS {DB_NAME}.{TABLE_NAME_DIST}
        ON CLUSTER {CLUSTER_NAME}
        (
            id UUID DEFAULT generateUUIDv4(),
            user_session Nullable(UUID),
            user_uuid Nullable(UUID),
            user_agent String,
            ip_address Nullable(String),
            film_uuid Nullable(UUID),
            event_params Map(String, String),
            event_type String,
            message_event String,
            event_timestamp DateTime,
            user_timestamp DateTime
        )
        ENGINE = Distributed(
            '{CLUSTER_NAME}',
            '{DB_NAME}',
            '{TABLE_NAME}',
            rand()
        )
    """.format(
            DB_NAME=DB_NAME,
            TABLE_NAME_DIST=TABLE_NAME_DIST,
            CLUSTER_NAME=CLUSTER_NAME,
            TABLE_NAME=TABLE_NAME,
        ),
    )


def main() -> None:
    import logging

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    try:
        client = Client(CLICKHOUSE_HOST, user=USER, password=PASSWORD)
        create_schema_metrics(client)
        create_schema_trends(client)
        logger.info("Инициализация базы данных выполнена успешно!")
    except errors.ServerException as error:
        logger.error(f"Возникло исключение при работе с сервером CH: {error}")
    finally:
        client.disconnect()
        logger.info("Соединение успешно закрыто")


if __name__ == "__main__":
    main()
