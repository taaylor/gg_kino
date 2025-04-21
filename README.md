# yandex_kinoservice
Киносервис
В корневой директории проекта:
```
docker compose up --build -d
docker compose exec postgres psql -U postgres -d pg_db
\dt
```
Вывод должен быть:
```
              List of relations
 Schema |      Name       | Type  |  Owner
--------+-----------------+-------+----------
 public | alembic_version | table | postgres
 public | example         | table | postgres
 public | example_2       | table | postgres
(3 rows)
```


Для создания пользователя через терминал сначала нужно запустить docker compose:
```
docker compose up --build -d
```
Создание суперпользователя через терминал:
```
bash scripts/create_superuser.sh
```
или
```
docker compose exec auth-api python manage.py createsuperuser
```
