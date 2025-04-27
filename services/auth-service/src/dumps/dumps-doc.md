# Директория содержит в себе dump данных для postgres

Чтобы выполнить dump таблиц: dict_roles, roles_permissions
необходимо подключится к БД локально и выполнить команды
```
yandex_kinoservice/auth-service/src$ psql -h localhost -p 5432 -U postgres -d pg_db -c "\copy profile.dict_roles FROM 'dumps/roles.csv' DELIMITER ',' CSV HEADER"
```
```
yandex_kinoservice/auth-service/src$ psql -h localhost -p 5432 -U postgres -d pg_db -c "\copy profile.roles_permissions FROM 'dumps/permissions.csv' DELIMITER ',' CSV HEADER"
```
