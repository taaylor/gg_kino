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

COPY services/notification-service/src/pyproject.toml services/notification-service/src/poetry.lock ./

COPY libs/auth_utils /opt/app/libs/auth_utils
RUN cd /opt/app/libs/auth_utils && poetry build && cd /opt/app && poetry add libs/auth_utils

COPY libs/tracer_utils /opt/app/libs/tracer_utils
RUN cd /opt/app/libs/tracer_utils && poetry build && cd /opt/app && poetry add libs/tracer_utils

RUN poetry install --only main && useradd -m notifiuser

COPY services/notification-service/src .

RUN chmod +x ./scripts/entrypoint.sh

USER notifiuser

ENTRYPOINT ["./scripts/entrypoint.sh"]
