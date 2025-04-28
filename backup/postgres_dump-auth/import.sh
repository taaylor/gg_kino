#!/bin/bash

# Ожидание доступности PostgreSQL
until pg_isready -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER}; do
  echo "Ожидание PostgreSQL..."
  sleep 5
done

# Импорт данных из roles.csv в таблицу profile.dict_roles
psql -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DB} -c "\copy profile.dict_roles FROM '/app/roles.csv' DELIMITER ',' CSV HEADER"

# Импорт данных из permissions.csv в таблицу profile.permissions
psql -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DB} -c "\copy profile.permissions FROM '/app/permissions.csv' DELIMITER ',' CSV HEADER"
