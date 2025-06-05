FROM python:3.12-slim

RUN apt-get update && apt-get install -y clickhouse-client && rm -rf /var/lib/apt/lists/*

RUN pip install clickhouse-driver dotenv

COPY ./init_struct.py ./

CMD [ "python", "init_struct.py" ]
