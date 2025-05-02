#!/bin/bash

# Ожидание доступности PostgreSQL
until pg_isready -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER}; do
  echo "Ожидание PostgreSQL..."
  sleep 5
done

# Функция для проверки количества строк в таблице
check_table_rows() {
  local table=$1
  local count=$(psql -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DB} -t -c "SELECT COUNT(*) FROM $table")
  echo $count
}

# Проверка и импорт для profile.dict_roles
if [ $(check_table_rows "profile.dict_roles") -eq 0 ]; then
  psql -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DB} -c "\copy profile.dict_roles FROM '/app/roles.csv' DELIMITER ',' CSV HEADER"
  echo "Данные импортированы в profile.dict_roles"
else
  echo "Данные в profile.dict_roles уже существуют, пропускаем импорт"
fi

# Проверка и импорт для profile.roles_permissions
if [ $(check_table_rows "profile.roles_permissions") -eq 0 ]; then
  psql -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DB} -c "\copy profile.roles_permissions FROM '/app/permissions.csv' DELIMITER ',' CSV HEADER"
  echo "Данные импортированы в profile.roles_permissions"
else
  echo "Данные в profile.roles_permissions уже существуют, пропускаем импорт"
fi
