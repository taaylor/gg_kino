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

COPY services/async-api/src/pyproject.toml services/async-api/src/poetry.lock ./

RUN poetry install --without test && which gunicorn

COPY services/async-api/src/ .

CMD ["gunicorn", "main:app", "--config", "./core/gunicorn_conf.py"]
