FROM debian:bookworm-slim

# Установка postgresql-client
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование файлов для импорта
# COPY ./postgres_dump-auth/roles.csv /app/roles.csv
# COPY ./postgres_dump-auth/permissions.csv /app/permissions.csv
# COPY ./postgres_dump-auth/import.sh /app/import.sh
COPY backup/postgres_dump-auth/roles.csv /app/roles.csv
COPY backup/postgres_dump-auth/permissions.csv /app/permissions.csv
COPY backup/postgres_dump-auth/import.sh /app/import.sh


# Делаем скрипт исполняемым
RUN chmod +x /app/import.sh

# Запуск скрипта импорта
CMD ["/app/import.sh"]
