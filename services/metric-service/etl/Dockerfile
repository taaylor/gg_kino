FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl build-essential netcat-openbsd \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && export PATH="/root/.local/bin:$PATH" \
    && poetry config virtualenvs.create false

ENV PATH="/root/.local/bin:${PATH}"

COPY services/metric-service/etl/pyproject.toml services/metric-service/etl/poetry.lock ./



COPY requirements.txt requirements.txt
COPY .env .env

RUN  pip install --no-cache-dir --upgrade pip \
     && pip install -r requirements.txt

COPY ./etl .


CMD [ "python", "main.py" ]
