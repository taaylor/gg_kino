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

# Копируем auth_utils
# COPY libs/auth_utils /opt/auth_utils/
# RUN cd /opt/auth_utils && poetry build && pip install dist/*.whl

COPY .env ./
COPY services/auth-service/src/pyproject.toml services/auth-service/src/poetry.lock ./

RUN poetry install --only main

COPY services/auth-service/src/ .

RUN chmod +x ./scripts/entrypoint.sh

CMD ["./scripts/entrypoint.sh"]
