ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    netcat-openbsd \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /opt/app

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && export PATH="/root/.local/bin:$PATH" \
    && poetry config virtualenvs.create false

ENV PATH="/root/.local/bin:${PATH}"

COPY services/ws_notification-service/src/pyproject.toml services/ws_notification-service/src/poetry.lock ./

RUN poetry install --only main && useradd -m wsuser

COPY services/ws_notification-service/src .

USER wsuser

ENTRYPOINT ["gunicorn", "main:app", "--config", "./core/gunicorn_conf.py"]
