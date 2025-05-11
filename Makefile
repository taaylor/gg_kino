COMPOSE_FILE = docker-compose.yml
COMPOSE_FILE_DEBUG = docker-compose.debug.yml
COMPOSE_FILE_TEST = docker-compose-tests.yml

# Можно указать конкретный серви или не указывать и команда будет выполнена для всех сервисов
# Например: make up-logs srv=auth-api
srv ?=

# Запуск контейнеров в фоновом режиме
up:
	docker-compose -f $(COMPOSE_FILE) up -d $(srv)

# Остановка контейнеров
down:
	docker-compose -f $(COMPOSE_FILE) down $(srv)

# Остановка контейнеров и удаление волуме
down-v:
	docker-compose -f $(COMPOSE_FILE) down -v $(srv)

up-logs:
	docker-compose -f $(COMPOSE_FILE) up -d --build && docker-compose -f $(COMPOSE_FILE) logs -f $(srv)

# Сборка образов
build:
	docker-compose -f $(COMPOSE_FILE) build

# Просмотр логов
logs:
	docker-compose -f $(COMPOSE_FILE) logs -f $(srv)

# Выполнение миграций (для Django, например)
migrate:
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py migrate

# Очистка (остановка и удаление томов)
clean:
	docker-compose -f $(COMPOSE_FILE) down -v

.PHONY: up down build logs migrate clean
