FROM python:3.12-slim

RUN apt-get update && apt-get install -y clickhouse-client && rm -rf /var/lib/apt/lists/*

RUN pip install clickhouse-driver dotenv

COPY backup/clickhouse_init_struct/init_struct.py ./

CMD [ "python", "init_struct.py" ]
